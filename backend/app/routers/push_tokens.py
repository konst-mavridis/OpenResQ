from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.firebase_config import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="", tags=["push-tokens"])

class PushToken(BaseModel):
    push_token: str

@router.post("/push-token")
def save_push_token(data: PushToken, user=Depends(get_current_user)):
    db = get_db()

    db.collection("users").document(user["uid"]).update({
        "push_token": data.push_token
    })

    return {"status": "ok"}
