<<<<<<< HEAD
"""
Reports/Incidents router - unified endpoint for report creation, retrieval, and updates.
All business logic is delegated to ReportService.
"""
from fastapi import APIRouter, Depends, HTTPException
import logging
from typing import List, Optional
from app.services.report_service import ReportService
from app.utils.verify import verify_token, require_role
from app.schemas.report import CreateReport, UpdateReport
from app.utils.logger import log_action
from app.utils.ws_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])
report_service = ReportService()


@router.post("/", response_model=dict)
def create_report(
    data: CreateReport,
    user=Depends(verify_token)
):
    """
    Create a new incident/report.
    
    Args:
        data: Report creation data
        user: Authenticated user context
    
    Returns:
        Created report with ID
    """
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
        try:
            import asyncio
            asyncio.create_task(
                ws_manager.broadcast({
                    "type": "new_report",
                    "report_id": report["id"],
                    "report": report
                })
            )
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed: {e}")
        
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nearby")
def get_nearby_reports(user=Depends(verify_token)):
    """
    Get reports near user's location.
    
    Returns:
        List of nearby reports
    """
    try:
        reports = report_service.get_nearby_reports(user["uid"])
        return reports
    except Exception as e:
        logger.error(f"Failed to get nearby reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")


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

=======
from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import db, fcm
from app.utils.verify import verify_token
from app.utils.roles import require_any, require_roles
from app.schemas.report import CreateReport, UpdateReport
from app.utils.geo import is_within_radius
from app.utils.ws_manager import ws_manager
from datetime import datetime
import uuid
from typing import List
from firebase_admin import firestore as admin_fs

router = APIRouter(prefix="/reports", tags=["Reports"])

# Create report - notify via websocket + FCM
@router.post("/", response_model=dict)
def create_report(data: CreateReport, user=Depends(require_any("citizen","responder","admin"))):
    report_id = str(uuid.uuid4())
    doc = {
        "uid": user["uid"],
        "title": data.title,
        "description": data.description,
        "event_type": data.event_type,
        "severity": data.severity,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "media": data.media or [],
        "status": "pending",
        "responder_notes": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    db.collection("reports").document(report_id).set(doc)

    # websocket broadcast (simple broadcast for now)
    # the clients will filter by role/area client-side or server-side in advanced impl
    try:
        import asyncio
        asyncio.create_task(ws_manager.broadcast({"type":"new_report","report_id":report_id,"report":doc}))
    except Exception:
        pass

    # FCM: send a notification to topic "responders" to alert responders
    # (Requires clients to subscribe to "responders" topic)
    try:
        message = fcm.Message(
            notification=fcm.Notification(title="New incident", body=f"{data.event_type} - {data.severity}"),
            topic="responders",
            data={"report_id": report_id}
        )
        fcm.send(message)
    except Exception:
        pass

    return {"message": "Report created", "report_id": report_id}


# nearby reports for citizen (within their area)
@router.get("/nearby", response_model=List[dict])
def nearby_reports(user=Depends(require_any("citizen","responder","admin"))):
    user_doc = db.collection("users").document(user["uid"]).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    if user["role"] == "citizen":
        area = user_data.get("area", {})
        center_lat = area.get("lat")
        center_lng = area.get("lng")
        radius = area.get("radius_km", 20.0)
    else:
        center_lat = center_lng = radius = None

    res = []
    for r in db.collection("reports").stream():
        d = r.to_dict()
        lat = d.get("latitude")
        lng = d.get("longitude")
        if user["role"] == "citizen":
            if not is_within_radius(center_lat, center_lng, lat, lng, radius):
                continue
        d["id"] = r.id
        res.append(d)
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
    return res

# assigned reports for responder
@router.get("/assigned", response_model=List[dict])
def assigned_reports(user=Depends(require_roles("responder","admin"))):
    user_doc = db.collection("users").document(user["uid"]).get()
    if not user_doc.exists:
        raise HTTPException(404, "User not found")
    u = user_doc.to_dict()
    area = u.get("area", {})
    center_lat = area.get("lat")
    center_lng = area.get("lng")
    radius = area.get("radius_km", 20.0)

    res = []
    for r in db.collection("reports").stream():
        d = r.to_dict()
        if is_within_radius(center_lat, center_lng, d.get("latitude"), d.get("longitude"), radius):
            d["id"] = r.id
            res.append(d)
    return res

# get single report
@router.get("/{report_id}", response_model=dict)
def get_report(report_id: str, user=Depends(verify_token)):
    doc = db.collection("reports").document(report_id).get()
    if not doc.exists:
        raise HTTPException(404, "Report not found")
    r = doc.to_dict()
    r["id"] = doc.id
    return r

# responder update - includes FCM + websocket broadcast
@router.patch("/{report_id}/respond", response_model=dict)
def responder_update(report_id: str, data: UpdateReport, user=Depends(require_roles("responder","admin"))):
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
        updates["updated_at"] = datetime.utcnow()
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
