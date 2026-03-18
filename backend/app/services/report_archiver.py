from firebase_admin import db, firestore
from datetime import datetime, timedelta
from app.firebase_config import get_db

db = get_db()

def move_to_historical(report_id: str, data: dict):
    db.collection("historical_reports").document(report_id).set({
        **data,
        "moved_at": datetime.utcnow()
    })
    db.collection("reports").document(report_id).delete()


def archive_old_reports():
    now = datetime.utcnow()

    # 1) ACTIVE reports older than 48 hours
    active_reports = db.collection("reports") \
        .where("status", "==", "active") \
        .stream()

    for doc in active_reports:
        data = doc.to_dict()
        created_at = data.get("created_at")
        if not created_at:
            continue

        age_hours = (now - created_at).total_seconds() / 3600
        if age_hours >= 48:
            move_to_historical(doc.id, data)

    # 2) RESOLVED reports older than 24 hours
    resolved_reports = db.collection("reports") \
        .where("status", "==", "resolved") \
        .stream()

    for doc in resolved_reports:
        data = doc.to_dict()
        resolved_at = data.get("resolved_at")
        if not resolved_at:
            continue

        age_hours = (now - resolved_at).total_seconds() / 3600
        if age_hours >= 24:
            move_to_historical(doc.id, data)
