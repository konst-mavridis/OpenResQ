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
