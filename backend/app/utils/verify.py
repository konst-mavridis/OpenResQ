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
    """
    Verify Firebase ID token and return user context.
    
    Args:
        authorization: Authorization header with Bearer token
    
    Returns:
        User context dictionary with uid, email, role, etc.
    
    Raises:
        HTTPException: If token is missing, invalid, or verification fails
    """
    token = _get_bearer_token(authorization)
    
    if not token:
        log_action(logger, "authentication", "failed", details={"reason": "missing_token"})
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    try:
        # Verify Firebase ID token
        auth = get_auth()
        decoded = auth.verify_id_token(token)
        
        uid = decoded.get("uid") or decoded.get("sub")
        if not uid:
            raise ValueError("No user ID in token")
        
        # Get user profile from Firestore
        db = get_db()
        user_doc = db.collection("users").document(uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            role = user_data.get("role", "citizen")
            area = user_data.get("area", {})
            if "trust_score" not in user_data:
                # Default trust score
                user_data["trust_score"] = 0.5
        else:
            # Create default user profile if doesn't exist
            role = "citizen"
            area = {
                "latitude": 37.9838,
                "longitude": 23.7275,
                "radius_km": 20.0
            }
            default_profile = {
                "uid": uid,
                "email": decoded.get("email"),
                "display_name": decoded.get("name", "Anonymous"),
                "role": role,
                "area": area,
                "trust_score": 0.5,
                "created_at": datetime.utcnow()
            }
            db.collection("users").document(uid).set(default_profile)
        
        user_context = {
            "uid": uid,
            "email": decoded.get("email"),
            "display_name": decoded.get("name", "Anonymous"),
            "role": role,
            "area": area
        }
        
        return user_context
        
    except Exception as e:
        log_action(
            logger,
            "authentication",
            "failed",
            details={"reason": "token_verification_error", "error": str(e)}
        )
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


