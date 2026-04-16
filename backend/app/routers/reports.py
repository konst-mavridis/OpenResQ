"""
Reports/Incidents router - unified endpoint for report creation, retrieval, and updates.
All business logic is delegated to ReportService.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
import time 
import queue
import threading
import logging
from typing import List, Optional
import datetime
import firebase_admin.firestore as admin_fs
from app.firebase_config import db, fcm
from app.services.fcm_service import send_push_to_token
from app.services.report_service import ReportService
from app.utils.verify import verify_token, require_role
from app.dependencies.subscription import check_report_limit
from app.schemas.report import CreateReport, PushTokenCreate, UpdateReport, ChatMessageCreate
from app.utils.logger import log_action
from app.utils.ws_manager import ws_manager
from app.utils.geo import haversine_distance_km, is_within_radius
from firebase_admin import firestore, storage
from ..services.validation_service import calculate_confidence, InputValidator
from ..services.incident_matcher import find_similar_reports
from ..services.ai_service import predict_fire  
import base64
import openai
import os 
import requests
import asyncio
from ..services.trust_service import TrustService
from ..services.user_service import UserRepository
from typing import Optional
from ..services.priority_service import get_service_priority


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()
firestore_listeners = {}


def haversine_distance(lat1, lon1, lat2, lon2):
    return report_service.haversine_distance(lat1, lon1, lat2, lon2)


def _increment_stats(uid: str, field: str):
    user_ref = db.collection("users").document(uid)
    stats_ref = user_ref.collection("stats").document("dispatch_stats")

    # increment in user document
    user_ref.set({
        field: firestore.Increment(1)
    }, merge=True)

    # increment in stats document
    stats_ref.set({
        field: firestore.Increment(1)
    }, merge=True)


def _tx_inc(tx, user_ref, stats_ref, field: str):
    user_doc = tx.get(user_ref)
    stats_doc = tx.get(stats_ref)

    user_data = user_doc.to_dict() if user_doc.exists else {}
    stats_data = stats_doc.to_dict() if stats_doc.exists else {}

    user_val = int(user_data.get(field, 0)) + 1
    stats_val = int(stats_data.get(field, 0)) + 1

    tx.set(user_ref, {field: user_val}, merge=True)
    tx.set(stats_ref, {field: stats_val}, merge=True)


def _has_active_report(uid: str) -> bool:
    queries = [
        db.collection("reports")
        .where("assignedTo", "==", uid)
        .where("status", "in", ["assigned", "in_progress"])
        .limit(1),
        db.collection("reports")
        .where("assigned_to", "==", uid)
        .where("status", "in", ["assigned", "in_progress"])
        .limit(1),
    ]

    for query in queries:
        if any(True for _ in query.stream()):
            return True
    return False

openai.api_key = os.getenv("OPENAI_API_KEY")  # set στο environment


def start_reports_listener(user_id: str, q):
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            doc = change.document

            # 🔹 μόνο τα changed fields
            update_mask = {}
            if change.type.name == "MODIFIED":
                for field in doc._data:
                    update_mask[field] = doc.get(field)

            payload = {
                "type": change.type.name,  # ADDED / MODIFIED / REMOVED
                "id": doc.id,
                "data": update_mask if update_mask else doc.to_dict()
            }

            q.put(json.dumps(payload))

    query = db.collection("reports").where("deleted", "!=", True)
    firestore_listeners[user_id] = query.on_snapshot(on_snapshot)


def predict_fire_openai(image_url: str) -> dict:
    """
    Καλεί OpenAI Vision για να εντοπίσει φωτιά σε εικόνα.
    Επιστρέφει: {"fire": True/False, "confidence": 0.0-1.0}
    """
    try:
        # Κατέβασε εικόνα
        resp = requests.get(image_url)
        resp.raise_for_status()
        img_b64 = base64.b64encode(resp.content).decode("utf-8")

        prompt = (
            "You are an AI that detects fire in images. "
            "The image is provided as base64. "
            "Respond ONLY in JSON format with keys 'fire' (true/false) and 'confidence' (0.0-1.0)."
        )

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Image (base64): {img_b64}"}
            ]
        )

        # ✅ Το σωστό για GPT-4o-mini: choices[0].message.content
        text = response.choices[0].message.content
        if not text:
            raise ValueError("Empty response from OpenAI")
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            print(f"[AI ERROR] Cannot parse OpenAI JSON: {text}")
            result = {"fire": False, "confidence": 0.0}

    except Exception as e:
        print(f"[AI ERROR] OpenAI prediction failed: {e}")
        return {"fire": False, "confidence": 0.0} 

def severity_score(sev: Optional[str]) -> int:
    return {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }.get(sev or "", 0)


def sort_reports_for_responder(reports, responder, lat, lng):
    # π.χ. responder.service_id = "fire_department"
    service_id = responder.service_id
    priorities = get_service_priority(service_id)

    def type_priority(event_type: Optional[str]) -> int:
        return priorities.get(event_type or "", 999)

    def dist(r):
        return haversine_distance_km(lat, lng, r.latitude, r.longitude)

    reports.sort(
        key=lambda r: (
            -severity_score(r.severity),
            type_priority(r.event_type),
            dist(r),
        )
    )
    return reports


@router.post("/", response_model=dict)
async def create_report(
    data: CreateReport,
    user=Depends(verify_token),
    org=Depends(check_report_limit)
):
    try:
        print("[DEBUG] Received report data:", data.dict())
        print("[DEBUG] User:", user)
        print("[DEBUG] Org:", org.get("id"))

        # ==========================
        # 1) INPUT VALIDATION
        # ==========================
        from app.services.validation_service import InputValidator

        InputValidator.validate_report(
            title=data.title,
            description=data.description,
            event_type=data.event_type,
            severity=data.severity,
            latitude=data.latitude,
            longitude=data.longitude
        )
        print("[DEBUG] Input validation passed")

        # ==========================
        # 2) DUPLICATE CHECK
        # ==========================
        recent_reports = report_service.get_recent_reports(hours=2)

        for r in recent_reports:
            if (
                r.get("title") == data.title and
                abs(r.get("latitude") - data.latitude) < 0.0005 and
                abs(r.get("longitude") - data.longitude) < 0.0005
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Similar report already exists nearby"
                )

        print("[DEBUG] Duplicate check passed")

        # ==========================
        # 3) BUSINESS RULES
        # ==========================

        # Fire reports must have media
        if data.event_type == "fire" and not data.media:
            raise HTTPException(
                status_code=400,
                detail="Fire reports require at least one image"
            )

        # Low trust users cannot submit reports
        if user.get("trust_score", 1.0) < 0.2:
            raise HTTPException(
                status_code=403,
                detail="Your trust score is too low to submit reports"
            )
        repo=UserRepository(db)
        # Trust service check
        trust_service = TrustService(repo)

        if not trust_service.can_submit(user["uid"], data.event_type):
            raise HTTPException(status_code=403, detail="Your trust score is too low to submit this type of report")

        # Μετά την δημιουργία του report και AI analysis

        # ==========================
        # 4) UPLOAD MEDIA
        # ==========================
        uploaded_media = []

        if data.media:
            for idx, m in enumerate(data.media):
                print(f"[DEBUG] Uploading image {idx}: {m}")
                uploaded_url = report_service.upload_image_to_firebase(m["url"])
                uploaded_media.append({
                    "url": uploaded_url,
                    "type": m.get("type", "image")
                })
                print(f"[UPLOAD] Uploaded {idx}: {uploaded_url}")
        else:
            print("[DEBUG] No media to upload")

        # ==========================
        # 5) RUN AI VISION (IF IMAGE)
        # ==========================
        ai_score = 0.0
        ai_fire_detected = False

        if uploaded_media:
            first_image_url = uploaded_media[0]["url"]
            print(f"[DEBUG] Running AI on: {first_image_url}")

            ai_result = report_service.run_ai_analysis(first_image_url)

            ai_fire_detected = ai_result["fire"]
            ai_score = ai_result["confidence"]

            print(f"[AI] score={ai_score}, fire={ai_fire_detected}")

        # If AI is 0 confidence and event is fire → soft warning
        if data.event_type == "fire" and ai_score < 0.1:
                print("[WARNING] Low AI confidence for fire report")

                trust_service.apply_report_feedback(
            user_id=user["uid"],
            report_verified=True if ai_score > 0.7 else False,
            ai_confidence=ai_score
        )

        # ==========================
        # 6) CREATE REPORT
        # ==========================
        report = report_service.create_report(
            user_id=user["uid"],
            title=data.title,
            description=data.description,
            event_type=data.event_type,
            severity=data.severity,
            latitude=data.latitude,
            longitude=data.longitude,
            media=uploaded_media,
            ai_score=ai_score,
            ai_fire_detected=ai_fire_detected,
            org_id=org.get("id")
        )

        print("[DEBUG] Report created:", report["id"])
        distance_km = haversine_distance_km(user["lat"], user["lng"], data.latitude, data.longitude)
        if distance_km <= 20: 
            token = user.get("fcm_token")
            if token:
                send_push_to_token(
                    token, 
                    "New Incident Nearby", 
                    f"Severity: {data.severity}", 
                    data={"incident_id": report["id"]}
                )

        # ==========================
        # 7) CALCULATE CONFIDENCE
        # ==========================
        from app.services.validation_service import calculate_confidence

        similar_reports = find_similar_reports(
            data.latitude,
            data.longitude,
            recent_reports,
            radius_km=0.1
        )

        confidence = calculate_confidence(
            report=report,
            nearby_reports=len(similar_reports),
            user_trust=user.get("trust_score", 0.5),
            community_confirms=0,
            ai_fire_score=ai_score
        )

        report_service.update_report(
            report_id=report["id"],
            updates={"confidence": confidence}
        )

        print(f"[DEBUG] Confidence calculated: {confidence}")

        # ==========================
        # 8) WEBSOCKET BROADCAST
        # ==========================
        await asyncio.create_task(ws_manager.broadcast({
            "type": "new_report",
            "report_id": report["id"],
            "report": report
        }))

        print("[DEBUG] WebSocket broadcast done")

        return report

    except Exception as e:
        print("[ERROR] Failed to create report:", e)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/nearby")
def get_nearby_reports(user=Depends(verify_token)):

    try:
        reports = report_service.get_nearby_reports(user["uid"])
        return reports


    except Exception as e:
        logger.error(f"Failed to get nearby reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")

@router.get("/nearby/live")
def live_nearby_reports(user=Depends(verify_token)):
    user_id = user["uid"]
    q = queue.Queue()

    start_reports_listener(user_id, q)

    def stream():
        try:
            while True:
                if not q.empty():
                    yield f"data: {q.get()}\n\n"
                time.sleep(0.25)
        except GeneratorExit:
            listener = firestore_listeners.pop(user_id, None)
            if listener:
                listener()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/all", response_model=List[dict])
def all_reports(user=Depends(verify_token)):
    res = []
    for r in db.collection("reports").stream():  # χωρίς where
        d = r.to_dict()
        # Αν το πεδίο deleted δεν υπάρχει ή είναι False, θεωρείται ενεργό
        if d.get("deleted") is not True:
            d["id"] = r.id
            res.append(d)
    return res

# assigned reports for responder
@router.get("/assigned", response_model=List[dict])
def assigned_reports(user=Depends(require_role("responder","admin"))):
    uid = user["uid"]

    # Fetch only reports assigned to this responder
    reports = db.collection("reports") \
        .where("assignedTo", "==", uid) \
        .where("status", "==", "assigned") \
        .stream()

    result = []
    for r in reports:
        data = r.to_dict()
        data["id"] = r.id
        result.append(data)

    return result

@router.get("/{report_id}")
def get_report(report_id: str, user=Depends(verify_token)):
    """Get a specific report by ID."""
    try:
        report = report_service.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{report_id}/status")
def update_report_status(
    report_id: str,
    status: str,
    responder=Depends(require_role("responder", "admin"))
):
    """
    Update report status (responder/admin only).
    
    Args:
        report_id: Report ID
        status: New status
        responder: Responder/admin user context
    
    Returns:
        Success message
    """
    valid_statuses = ["pending", "in_progress", "resolved", "closed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        report_service.update_report_status(
            report_id,
            status,
            responder["uid"]
        )
        return {"message": f"Report status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{report_id}/claim", response_model=dict)
async def claim_report(report_id: str, user=Depends(require_role("responder","admin"))):
    """
    Assign the report to the current responder.
    Once claimed, no other responder can claim it.
    """
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "Report not found")

    report = doc.to_dict()

    if report.get("assigned_to"):
        raise HTTPException(400, f"Report already assigned to {report['assigned_to']}")

    # assign to current responder
    doc_ref.update({
        "assigned_to": user["uid"],
        "assigned_at": datetime.datetime.utcnow()
    })

    # websocket broadcast
    import asyncio
    await asyncio.create_task(ws_manager.broadcast({
        "type": "report_assigned",
        "report_id": report_id,
        "assigned_to": user["uid"]
    }))

    return {"message": f"Report assigned to {user['uid']}"}

@router.post("/{report_id}/notes")
def add_responder_note(
    report_id: str,
    note: str,
    responder=Depends(require_role("responder", "admin"))
):
    """
    Add a responder note to a report.
    
    Args:
        report_id: Report ID
        note: Note text
        responder: Responder/admin user context
    
    Returns:
        Success message
    """
    try:
        report_service.add_responder_note(
            report_id,
            responder["uid"],
            note
        )
        return {"message": "Note added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return res

# responder update - includes FCM + websocket broadcast
@router.patch("/{report_id}/respond", response_model=dict)
def responder_update(report_id: str, data: UpdateReport, user=Depends(require_role("responder","admin"))):
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "Report not found")
    updates = data.dict(exclude_unset=True)

    # handle responder_note separately (append)
    note = updates.pop("responder_note", None)
    if note:
        # Firestore ArrayUnion requires firebase_admin.firestore import alias
        doc_ref.update({"responder_notes": admin_fs.ArrayUnion([{"user": user["uid"], "note": note, "ts": datetime.utcnow()}])})

    if updates:
        updates["updated_at"] = datetime.datetime.utcnow()
        doc_ref.update(updates)

    # broadcast via websocket
    try:
        import asyncio
        asyncio.create_task(ws_manager.broadcast({"type":"report_update","report_id":report_id,"updates":updates}))
    except Exception:
        pass

    # FCM: notify topic "citizens" maybe, or specific subscribers
    try:
        message = fcm.Message(
            notification=fcm.Notification(title="Report updated", body=f"{updates.get('status','updated')}"),
            topic="citizens",
            data={"report_id": report_id}
        )
        fcm.send(message)
    except Exception:
        pass

    return {"message": "Updated by responder"}


@router.patch("/{report_id}/edit")
def edit_own_report(
    report_id: str,
    data: UpdateReport,
    user=Depends(verify_token)
):
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "Report not found")

    report = doc.to_dict()

    if report.get("status") == "resolved":
        raise HTTPException(400, "Resolved reports cannot be deleted")

    # 🔐 ownership check
    if report.get("uid") != user["uid"]:
        raise HTTPException(403, "Not your report")

    # ❌ αν έχει διαγραφεί
    if report.get("deleted") is True:
        raise HTTPException(400, "Report is deleted")

    updates = data.dict(exclude_unset=True)
    updates["updated_at"] = datetime.datetime.utcnow()

    doc_ref.update(updates)

    log_action(
        logger,
        action="edit_own_report",
        status="success",
        user_id=user["uid"],
        resource_id=report_id,
        details={"fields": list(updates.keys())},
    )

    return {"message": "Report updated"}


@router.delete("/{report_id}/delete")
def delete_own_report(
    report_id: str,
    reason: str = "Deleted by user",
    user=Depends(verify_token)
):
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "Report not found")

    report = doc.to_dict()

    # 🔐 ownership check
    if report.get("uid") != user["uid"]:
        raise HTTPException(403, "Not your report")
    
    if report.get("status") == "resolved":
        raise HTTPException(400, "Resolved reports cannot be deleted")


    # 📦 archive πριν το delete
    db.collection("deleted_reports").document(report_id).set({
        **report,
        "deleted_at": datetime.datetime.utcnow(),
        "deleted_by": user["uid"],
        "deleted_by_role": "citizen",
        "delete_reason": reason,
        "delete_type": "hard"
    })

    # 🗑️ HARD DELETE
    doc_ref.delete()

    log_action(
        logger,
        action="user_hard_delete",
        status="success",
        user_id=user["uid"],
        resource_id=report_id,
        details={
            "reason": reason
        },
    )

    return {"message": "Report permanently deleted"}


# Chat
@router.post("/{report_id}/chat")
async def send_message(report_id: str, data: ChatMessageCreate, user=Depends(verify_token)):
    chat_ref = db.collection("chats").document(report_id)
    msg_ref = chat_ref.collection("messages").document()
    msg_ref.set({
        "text": data.text,
        "sender_id": user["uid"],
        "sender_role": user["role"],
        "created_at": datetime.datetime.utcnow()
    })

    # WebSocket broadcast
    import asyncio
    asyncio.create_task(ws_manager.broadcast({
        "type": "chat_message",
        "report_id": report_id,
        "message": {
            "id": msg_ref.id,
            "text": data.text,
            "sender_id": user["uid"],
            "sender_role": user["role"]
        }
    }))

    # FCM push
    try:
        message = fcm.Message(
            notification=fcm.Notification(title="New message", body=data.text),
            topic="chat_" + report_id,
            data={"report_id": report_id}
        )
        fcm.send(message)
    except Exception:
        pass

    return {"message": "sent"}


@router.get("/{report_id}/chat")
def get_messages(report_id: str, user=Depends(verify_token)):
    messages = (
        db.collection("chats")
        .document(report_id)
        .collection("messages")
        .order_by("created_at")
        .stream()
    )
    return [{**m.to_dict(), "id": m.id} for m in messages]

@router.post("/push-token")
def send_push_token(data: PushTokenCreate, user=Depends(verify_token)):
    db.collection("users").document(user["uid"]).set(
        {
            "push_tokens": firestore.ArrayUnion([data.token]),
            "updated_at": datetime.datetime.utcnow()
    }, merge=True)
    return {"message": "Push token saved"}

@router.post("/{report_id}/chat/seen")
def mark_seen(report_id: str, user=Depends(verify_token)):
    msgs = (
        db.collection("chats")
        .document(report_id)
        .collection("messages")
        .where("sender_id", "!=", user["uid"])
        .stream()
    )

    for m in msgs:
        m.reference.update({"seen": True})

    return {"status": "ok"}

@router.post("/{report_id}/resolve")
def resolve_report(
    report_id: str,
    responder_uid: str = Query(...)
):
    report_ref = db.collection("reports").document(report_id)
    report_doc = report_ref.get()

    if not report_doc.exists:
        raise HTTPException(404, "Report not found")

    report = report_doc.to_dict()

    if report.get("assignedTo") != responder_uid:
        raise HTTPException(400, "You are not assigned to this report")

    # Update report status and metadata
    report_ref.update({
        "status": "resolved",
        "resolved_by": responder_uid,
        "resolved_at": datetime.datetime.utcnow(),
        "assignedTo": firestore.DELETE_FIELD,
        "assigned_at": firestore.DELETE_FIELD,
        "on_hold_for": firestore.DELETE_FIELD,
        "on_hold_at": firestore.DELETE_FIELD
    })

    # Increment the user's resolved reports counter dynamically
    user_ref = db.collection("users").document(responder_uid)
    user_ref.update({
        "incidents_resolved": firestore.Increment(1),
        "resolved_reports": firestore.Increment(1)
    })
    
    # Apply to dispatch_stats subcollection as fallback
    stats_ref = user_ref.collection("stats").document("dispatch_stats")
    if stats_ref.get().exists:
        stats_ref.update({
            "incidents_resolved": firestore.Increment(1)
        })
    else:
        stats_ref.set({
            "incidents_resolved": 1
        })

    return {"status": "resolved", "report_id": report_id}


# ---------------------------------------------------------
# MANUAL UNASSIGN
# ---------------------------------------------------------
@router.post("/{report_id}/unassign")
def unassign_report(
    report_id: str,
    responder_uid: str = Query(...)
):
    report_ref = db.collection("reports").document(report_id)
    report_doc = report_ref.get()

    if not report_doc.exists:
        raise HTTPException(404, "Report not found")

    report = report_doc.to_dict()

    if report.get("assignedTo") != responder_uid:
        raise HTTPException(400, "You are not assigned to this report")

    report_ref.update({
        "status": "pending",
        "assignedTo": firestore.DELETE_FIELD,
        "assigned_at": firestore.DELETE_FIELD,
        "on_hold_for": firestore.DELETE_FIELD,
        "on_hold_at": firestore.DELETE_FIELD
    })

    return {"status": "pending", "report_id": report_id}

@router.post("/{report_id}/assign")
def manual_assign(
    report_id: str,
    responder_uid: str = Query(...)
):
    # Validate responder
    user_doc = db.collection("users").document(responder_uid).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Responder not found")

    user = user_doc.to_dict()
    if user.get("role") != "responder":
        raise HTTPException(status_code=400, detail="User is not a responder")
    if not user.get("on_duty", False):
        raise HTTPException(status_code=400, detail="Responder is OFF DUTY")

    # Check if responder already has an active report
    if _has_active_report(responder_uid):
        raise HTTPException(status_code=400, detail="Responder already has an active report")

    # Validate report
    report_ref = db.collection("reports").document(report_id)
    report_doc = report_ref.get()
    if not report_doc.exists:
        raise HTTPException(status_code=404, detail="Report not found")

    report = report_doc.to_dict()
    if report.get("status") not in ["pending", "unassigned", None, "community_verified"]:
        raise HTTPException(status_code=400, detail="Report is not available for assignment")

    now = datetime.datetime.utcnow()

    # Assign the report
    report_ref.update({
        "assignedTo": responder_uid,
        "status": "assigned",
        "assigned_at": now,
        "on_hold_for": firestore.DELETE_FIELD,
        "on_hold_at": firestore.DELETE_FIELD
    })

    # Update responder stats
    db.collection("users").document(responder_uid).update({
        "last_assigned_at": now
    })

    _increment_stats(responder_uid, "accepted_reports")

    return {
        "status": "assigned",
        "report_id": report_id,
        "responder": responder_uid
    }


@router.post("/suggest_for_responder")
def suggest_for_responder(
    responder_uid: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...)
):
    # ---------------------------------------------------------
    # 1) Load responder
    # ---------------------------------------------------------
    user_ref = db.collection("users").document(responder_uid)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(404, "Responder not found")

    user = user_doc.to_dict()

    if user.get("role") != "responder":
        raise HTTPException(400, "User is not a responder")

    if not user.get("on_duty", False):
        raise HTTPException(400, "Responder is OFF DUTY")

    # ---------------------------------------------------------
    # 2) Prevent double assignment
    # ---------------------------------------------------------
    if _has_active_report(responder_uid):
        return {"suggested": None}

    # Cooldown 1 hour
    last_assigned_at = user.get("last_assigned_at")
    if last_assigned_at:
        if hasattr(last_assigned_at, "to_datetime"):
            last_dt = last_assigned_at.to_datetime().replace(tzinfo=None)
        else:
            last_dt = last_assigned_at.replace(tzinfo=None)

        if datetime.datetime.utcnow() - last_dt < datetime.timedelta(hours=1):
            return {"suggested": None}

    # ---------------------------------------------------------
    # 3) Load service type priorities from Firestore
    # ---------------------------------------------------------
    service_id = user.get("service_id", "default")

    pr_doc = db.collection("service_priorities").document(service_id).get()
    if pr_doc.exists:
        type_priorities = pr_doc.to_dict().get("priorities", {})
    else:
        type_priorities = {}  # fallback: no priorities configured

    def get_type_priority(event_type: str):
        return type_priorities.get(event_type, 999)

    # ---------------------------------------------------------
    # 4) Load candidate reports
    # ---------------------------------------------------------
    reports = db.collection("reports") \
        .where("status", "in", ["pending", "unassigned"]) \
        .stream()

    candidates = []

    for d in reports:
        r = d.to_dict()
        r_id = d.id

        # Skip rejected
        if responder_uid in r.get("rejected_by", []):
            continue

        # Skip invalid coords
        r_lat = r.get("latitude")
        r_lng = r.get("longitude")
        if r_lat is None or r_lng is None:
            continue

        # Distance
        dist = haversine_distance(lat, lng, r_lat, r_lng)
        if dist < 0.3:
            continue

        # Severity
        sev = r.get("severity", "low")
        if isinstance(sev, str):
            sev_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            severity = sev_map.get(sev.lower(), 1)
        else:
            severity = int(sev)

        # Created at
        created_at = r.get("created_at") or datetime.datetime.utcnow()
        if hasattr(created_at, "to_datetime"):
            created_at = created_at.to_datetime()

        # Event type
        event_type = r.get("event_type", "unknown")

        candidates.append({
            "id": r_id,
            "severity": severity,
            "distance": dist,
            "created_at": created_at,
            "event_type": event_type,
            "type_priority": get_type_priority(event_type),
            "data": r
        })

    if not candidates:
        return {"suggested": None}

    # ---------------------------------------------------------
    # 5) SORTING LOGIC:
    #    1) severity DESC
    #    2) type priority ASC
    #    3) distance ASC
    #    4) created_at DESC
    # ---------------------------------------------------------
    candidates.sort(
        key=lambda x: (
            -x["severity"],
            x["type_priority"],
            x["distance"],
            -x["created_at"].timestamp()
        )
    )

    best = candidates[0]
    report_id = best["id"]

    # ---------------------------------------------------------
    # 6) Mark report on hold
    # ---------------------------------------------------------
    db.collection("reports").document(report_id).update({
        "on_hold_for": responder_uid,
        "on_hold_at": datetime.datetime.utcnow()
    })

    best["data"]["id"] = report_id

    return {
        "suggested": best["data"],
        "used_priorities": type_priorities,
        "service_id": service_id
    }

@router.post("/{report_id}/accept_suggest")
def accept_suggest(
    report_id: str,
    responder_uid: str = Query(...)
):
    report_ref = db.collection("reports").document(report_id)
    report_doc = report_ref.get()
    if not report_doc.exists:
        raise HTTPException(404, "Report not found")

    report = report_doc.to_dict()

    if report.get("on_hold_for") != responder_uid:
        raise HTTPException(400, "Report is not on hold for this responder")

    if _has_active_report(responder_uid):
        raise HTTPException(400, "Responder already has an active report")

    now = datetime.datetime.utcnow()

    report_ref.update({
        "assignedTo": responder_uid,
        "status": "assigned",
        "assigned_at": now,
        "on_hold_for": firestore.DELETE_FIELD,
        "on_hold_at": firestore.DELETE_FIELD
    })

    db.collection("users").document(responder_uid).update({
        "last_assigned_at": now
    })

    _increment_stats(responder_uid, "accepted_reports")

    return {"status": "assigned", "report_id": report_id}

