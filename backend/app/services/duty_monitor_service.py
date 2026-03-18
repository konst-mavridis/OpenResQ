from firebase_admin import firestore
from datetime import datetime, timedelta
from app.firebase_config import get_db
from app.utils.ws_manager import ws_manager

db = get_db()

def check_responder_activity():
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=45)

    docs = db.collection("users") \
        .where("role", "==", "responder") \
        .where("on_duty", "==", True) \
        .stream()

    for d in docs:
        data = d.to_dict()
        last_active = data.get("last_active")

        if not last_active:
            continue

        if last_active < cutoff:
            db.collection("users").document(d.id).update({
                "on_duty": False
            })

            ws_manager.broadcast_sync({
                "type": "responder_status",
                "data": {
                    "uid": d.id,
                    "on_duty": False
                }
            }, filter_by_role="admin")
