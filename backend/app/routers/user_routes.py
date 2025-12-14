from fastapi import APIRouter, Depends
from app.firebase_config import db
from app.utils.verify import verify_token

router = APIRouter()

@router.get("/me")
async def get_user(user = Depends(verify_token)):
    doc = db.collection("users").document(user["uid"]).get()
    return doc.to_dict()
