<<<<<<< HEAD
"""
DEPRECATED: This module is deprecated. Use /reports router instead.
Kept for backward compatibility during migration.
All functionality has been consolidated into the reports router.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.routers.reports import create_report as _create_report_service
from app.utils.verify import verify_token

router = APIRouter()

@router.post("/incidents/")
async def create_incident(report: dict, user: dict = Depends(verify_token)):
    """
    DEPRECATED: Use POST /reports/ instead.
    This endpoint is maintained for backward compatibility only.
    """
    # Convert to reports format and call reports router
    from app.schemas.report import CreateReport
    
    try:
        report_data = CreateReport(**report)
        return await _create_report_service(report_data, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

=======
from fastapi import APIRouter, Depends
from app.firebase_config import db
from firebase_admin import firestore
from app.utils.verify import verify_token
from app.schemas.report import CreateReport
from datetime import datetime

router = APIRouter()

@router.post("/")
async def create_incident(report: CreateReport, user: dict = Depends(verify_token)):
    uid = user["uid"]

    # Load user document OR auto-create
    doc_ref = db.collection("users").document(uid).get()
    user_data = doc_ref.to_dict() if doc_ref.exists else None

    if user_data is None:
        # Create default Firestore profile
        default_data = {
            "role": "citizen",
            "display_name": user.get("name", "Anonymous")
        }
        db.collection("users").document(uid).set(default_data)
        user_data = default_data

    # Store report
    new_doc = db.collection("reports").document()
    new_data = {
        "id": new_doc.id,
        "uid": uid,
        "title": report.title,
        "description": report.description,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "image_url": report.image_url,
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    new_doc.set(new_data)

    return {"message": "Report submitted", "report": new_data}
    return {"message": "Report submitted", "report": new_data}
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
