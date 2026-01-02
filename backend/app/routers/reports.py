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
from firebase_admin import firestore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()
firestore_listeners = {}

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


@router.post("/", response_model=dict)
async def create_report(
    data: CreateReport,
    user=Depends(verify_token)
):
    try:
        report = report_service.create_report(
            user_id=user["uid"],
            title=data.title,
            description=data.description,
            event_type=data.event_type,
            severity=data.severity,
            latitude=data.latitude,
            longitude=data.longitude,
            media=data.media
        )
        
        # Broadcast to WebSocket clients
        await ws_manager.broadcast({
                    "type": "new_report",
                    "report_id": report["id"],
                    "report": report
        })
        
        return report
    except Exception as e:
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
def claim_report(report_id: str, user=Depends(require_role("responder","admin"))):
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
    asyncio.create_task(ws_manager.broadcast({
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
