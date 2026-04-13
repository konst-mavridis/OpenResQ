from app.firebase_config import get_db, initialize_firebase
from app.constants import PLANS
import datetime

initialize_firebase()
db = get_db()
plan_info = PLANS["pro"]

doc_ref = db.collection("organizations").document("org_SjyElxoy")
print("current doc:", doc_ref.get().to_dict())

org_update = {
    "plan": "pro",
    "subscription_status": "active",
    "limits": plan_info.get("limits", {}),
    "features": plan_info.get("features", []),
    "manual_override": False,
    "updated_at": datetime.datetime.utcnow(),
}
doc_ref.set(org_update, merge=True)
print("\nupdated successfully!")
