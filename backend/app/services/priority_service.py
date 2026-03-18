from typing import Dict
from app.firebase_config import get_db

db = get_db()

def set_service_priority(service_id: str, priorities: dict):
    db.collection("service_priorities").document(service_id).set({
        "priorities": priorities
    }, merge=True)

def get_service_priority(service_id: str) -> Dict[str, int]:
    doc = db.collection("service_priorities").document(service_id).get()
    if not doc.exists:
        return {}
    data = doc.to_dict() or {}
    return data.get("priorities", {})
