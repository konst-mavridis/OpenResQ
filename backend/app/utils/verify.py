"""
Token verification and authentication utilities.
Handles Firebase ID token verification and user context extraction.
"""
from fastapi import HTTPException, Header
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from app.firebase_config import get_auth, get_db
from app.utils.logger import log_action

logger = logging.getLogger(__name__)


def _get_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2:
        return None
    
    if parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    token = _get_bearer_token(authorization)
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    try:
        auth = get_auth()
        decoded = auth.verify_id_token(token)
        
        uid = decoded.get("uid") or decoded.get("sub")
        if not uid:
            raise ValueError("No user ID in token")
        
        db = get_db()
        user_doc = db.collection("users").document(uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
        else:
            # Create default user
            user_data = {
                "uid": uid,
                "email": decoded.get("email"),
                "display_name": decoded.get("name", "Anonymous"),
                "role": "citizen",
                "area": {
                    "latitude": 37.9838,
                    "longitude": 23.7275,
                    "radius_km": 20.0
                },
                "trust_score": 0.5,
                "created_at": datetime.utcnow()
            }
            db.collection("users").document(uid).set(user_data)

        # Ensure trust_score exists
        if "trust_score" not in user_data:
            user_data["trust_score"] = 0.5

        # RETURN FULL FIRESTORE PROFILE
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def require_role(*allowed_roles):
    """
    Dependency factory for role-based access control.
    
    Args:
        allowed_roles: Roles that are allowed to access the endpoint
    
    Returns:
        Dependency function that checks user role
    """
    def _check_role(authorization: Optional[str] = Header(None)):
        user = verify_token(authorization)
        
        if user.get("role") not in allowed_roles:
            log_action(
                logger,
                "authorization",
                "failed",
                user_id=user.get("uid"),
                details={"required_role": allowed_roles, "user_role": user.get("role")}
            )
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return user
    
    return _check_role


