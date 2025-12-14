from fastapi import HTTPException, Header
from typing import Optional
from app.firebase_config import firebase_auth, db

def _get_bearer_token(authorization: Optional[str]):
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1]

def verify_token(authorization: Optional[str] = Header(None)):
    token = _get_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        decoded = firebase_auth.verify_id_token(token)
        uid = decoded.get("uid") or decoded.get("sub") or decoded.get("user_id")
        # fetch/create user doc
        doc_ref = db.collection("users").document(uid)
        doc = doc_ref.get()
        if doc.exists:
            u = doc.to_dict()
            role = u.get("role", "citizen")
            return {"uid": uid, "email": decoded.get("email"), "role": role}
        else:
            # create default citizen with area centered on Athens as example
            doc_ref.set({
                "uid": uid,
                "email": decoded.get("email"),
                "role": "citizen",
                "area": {"lat": 37.9838, "lng": 23.7275, "radius_km": 20.0}
            })
            return {"uid": uid, "email": decoded.get("email"), "role": "citizen"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token error: {e}")
