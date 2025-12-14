from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import db
from app.utils.roles import require_roles
from app.schemas.report import UpdateReport
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

# Promote a user to responder
@router.post("/promote/{user_id}")
def promote_user(user_id: str, admin=Depends(require_roles("admin"))):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "User not found")
    doc_ref.update({"role": "responder"})
    return {"message": "Promoted to responder"}

# Set responder area
@router.post("/responder/{user_id}/area")
def set_responder_area(user_id: str, area: dict, admin=Depends(require_roles("admin"))):
    # area: {lat: float, lng: float, radius_km: float}
    db.collection("users").document(user_id).update({"area": area})
    return {"message": "Responder area updated"}

# Delete a report
@router.delete("/report/{report_id}")
def delete_report(report_id: str, admin=Depends(require_roles("admin"))):
    db.collection("reports").document(report_id).delete()
    return {"message": "Report deleted"}

# Edit report (admin can change everything)
@router.patch("/report/{report_id}")
def admin_edit_report(report_id: str, data: UpdateReport, admin=Depends(require_roles("admin"))):
    doc_ref = db.collection("reports").document(report_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, "Report not found")
    updates = data.dict(exclude_unset=True)
    updates["updated_at"] = datetime.utcnow()
    doc_ref.update(updates)
    return {"message": "Report updated by admin"}
