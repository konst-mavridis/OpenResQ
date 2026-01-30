from fastapi import APIRouter, HTTPException
from app.firebase_config import get_db
from datetime import datetime

router = APIRouter(prefix="/adminr", tags=["admin"])
db = get_db()

@router.get("/reports/for-review")
def get_reports_for_admin():
    docs = db.collection("reports").where("needs_admin_review", "==", True).stream()
    reports = []

    for d in docs:
        r = d.to_dict()
        r["id"] = d.id
        reports.append(r)

    return reports


@router.post("/reports/{report_id}/decision")
def admin_decide(report_id: str, decision: str):
    if decision not in ["approved", "rejected"]:
        raise HTTPException(400, "Decision must be approved or rejected")

    db.collection("reports").document(report_id).update({
        "status": decision,
        "needs_admin_review": False,
        "updated_at": datetime.utcnow()
    })

    return {"status": "ok", "report": report_id, "decision": decision}
