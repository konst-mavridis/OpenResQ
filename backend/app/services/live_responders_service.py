from firebase_admin import firestore
from app.utils.ws_manager import ws_manager
from app.firebase_config import get_db

db = get_db()

def start_responder_listener():
    def on_snapshot(col_snapshot, changes, timestamp):
        for change in changes:
            data = change.document.to_dict()
            data["uid"] = change.document.id

            if change.type.name == "ADDED":
                ws_manager.broadcast_sync({
                    "type": "responder_added",
                    "data": data
                }, filter_by_role="admin")

            elif change.type.name == "MODIFIED":
                data = change.document.to_dict()
                data["uid"] = change.document.id

                ws_manager.broadcast_sync({
                    "type": "responder_status",
                    "data": {
                        "uid": data["uid"],
                        "on_duty": data.get("on_duty", False),
                        "area": data.get("area", {})
                    }
                }, filter_by_role="admin")


            elif change.type.name == "REMOVED":
                ws_manager.broadcast_sync({
                    "type": "responder_removed",
                    "uid": change.document.id
                }, filter_by_role="admin")

    db.collection("users").where("role", "==", "responder").on_snapshot(on_snapshot)
