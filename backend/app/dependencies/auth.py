from fastapi import Depends, HTTPException, Header
from firebase_admin import auth
from app.firebase_config import get_db

async def get_current_user(authorization: str = Header(None)):
    """
    Extract and verify Firebase ID token from Authorization header.
    Expected format: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header format")

    token = authorization.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]

        db = get_db()
        doc = db.collection("users").document(uid).get()

        if not doc.exists:
            raise HTTPException(404, "User profile not found")

        return doc.to_dict()

    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")
