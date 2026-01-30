"""
Reports/Incidents router - unified endpoint for report creation, retrieval, and updates.
All business logic is delegated to ReportService.
"""
from fastapi import APIRouter, Depends, HTTPException 
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
from app.services.report_service import ReportService
from app.utils.verify import verify_token, require_role
from app.schemas.report import CreateReport, PushTokenCreate, UpdateReport, ChatMessageCreate
from app.utils.logger import log_action
from app.utils.ws_manager import ws_manager
from app.utils.geo import is_within_radius
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()
firestore_listeners = {}
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

@router.post("/", response_model=dict)
async def create_report(data: CreateReport, user=Depends(verify_token)):
    try:
        print("[DEBUG] Received report data:", data.dict())
        print("[DEBUG] User:", user)

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

        trust_service = TrustService(db)

        if not trust_service.can_submit(user["uid"], data.event_type):
            raise HTTPException(status_code=403, detail="Your trust score is too low to submit this type of report")

        # Μετά την δημιουργία του report και AI analysis
        trust_service.apply_report_feedback(
            user_id=user["uid"],
            report_verified=True if ai_score > 0.7 else False,
            ai_confidence=ai_score
        )
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
        )

        print("[DEBUG] Report created:", report["id"])

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

# assigned reports for responder
@router.get("/assigned", response_model=List[dict])
def assigned_reports(user=Depends(require_role("responder","admin"))):
    user_doc = db.collection("users").document(user["uid"]).get()
    if not user_doc.exists:
        raise HTTPException(404, "User not found")
    u = user_doc.to_dict()
    area = u.get("area", {})
    center_lat = area.get("lat")
    center_lng = area.get("lng")
    radius = area.get("radius_km", 20.0)

    res = []
    for r in db.collection("reports").where("deleted", "!=", True).stream():
        d = r.to_dict()
        if is_within_radius(center_lat, center_lng, d.get("latitude"), d.get("longitude"), radius):
            d["id"] = r.id
            res.append(d)
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
