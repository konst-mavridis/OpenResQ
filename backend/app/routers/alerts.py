from fastapi import APIRouter, Depends
from app.firebase_config import db
from app.utils.verify import verify_token

router = APIRouter()

@router.post("/")
async def send_alert(data: dict, user=Depends(verify_token)):
    alert_id = db.collection("alerts").document().id

    db.collection("alerts").document(alert_id).set({
        "id": alert_id,
        "title": data["title"],
        "message": data["message"],
        "timestamp": data.get("timestamp"),
        "level": data.get("level", 1)
    })

    return {"status": "alert sent", "id": alert_id}
