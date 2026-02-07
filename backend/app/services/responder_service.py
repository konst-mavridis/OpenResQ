from firebase_admin import firestore
from datetime import datetime
import logging
from app.utils.ws_manager import ws_manager
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class ResponderService:
    def __init__(self):
        self.db = firestore.client()

    def list_responders(self):
        responders = self.db.collection("users")\
            .where("role", "==", "responder")\
            .stream()

        return [
            {
                "uid": r.id,
                "display_name": r.to_dict().get("display_name", "Unknown"),
                **r.to_dict()
            }
            for r in responders
        ]

    def add_responder(self, uid: str):
        ref = self.db.collection("users").document(uid)

        if not ref.get().exists:
            raise Exception("User not found")

        ref.update({
            "role": "responder",
            "activated_at": datetime.utcnow()
        })

    def remove_responder(self, uid: str):
        ref = self.db.collection("users").document(uid)

        if not ref.get().exists:
            raise Exception("User not found")

        ref.update({
            "role": "user"
        })

    def toggle_active(self, uid: str, active: bool):
        self.db.collection("users").document(uid).update({
            "active": active
        })

    def get_display_name(self, uid: str) -> str:
        """Get user's display name from Firebase."""
        user_doc = self.db.collection("users").document(uid).get()
        if user_doc.exists:
            return user_doc.to_dict().get("display_name", "Unknown")
        return "Unknown"

    async def broadcast_responder_list(self):
        """Broadcast updated responder list to all admins via WebSocket."""
        responders = self.list_responders()
        await ws_manager.broadcast(
            {
                "type": "responder_list",
                "data": {"responders": responders},
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )

    async def broadcast_responder_activated(self, uid: str, responder_data: dict):
        """Broadcast responder activated event to all admins."""
        display_name = responder_data.get("display_name", self.get_display_name(uid))
        await ws_manager.broadcast(
            {
                "type": "responder_activated",
                "data": {
                    "uid": uid,
                    "display_name": display_name,
                    "responder": responder_data
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )

    async def broadcast_responder_deactivated(self, uid: str):
        """Broadcast responder deactivated event to all admins."""
        display_name = self.get_display_name(uid)
        await ws_manager.broadcast(
            {
                "type": "responder_deactivated",
                "data": {
                    "uid": uid,
                    "display_name": display_name
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )
