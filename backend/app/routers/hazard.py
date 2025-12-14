from fastapi import APIRouter, Depends
from app.schemas.hazard import HazardCreate
from app.firebase_config import db
from app.utils.verify import verify_token
from app.utils.roles import role_required
from firebase_admin import firestore

router = APIRouter(prefix="/hazards", tags=["hazards"])

@router.post("/")
def create_hazard(hazard: HazardCreate, user=Depends(verify_token)):
    doc_user = db.collection("users").document(user['uid']).get()
    user_role = doc_user.to_dict().get("role")
    role_required(user_role, ["responder", "admin"])
    doc_ref = db.collection("hazards").document()
    doc_ref.set({
        "type": hazard.type,
        "description": hazard.description,
        "location": hazard.location,
        "severity": hazard.severity,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return {"hazard_id": doc_ref.id}

@router.get("/")
def list_hazards():
    hazards = db.collection("hazards").stream()
    return [h.to_dict() | {"id": h.id} for h in hazards]
