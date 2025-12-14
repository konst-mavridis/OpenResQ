"""
Authentication routes - handles user registration, deletion, and role management.
All business logic is delegated to AuthService.
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
from app.services.auth_service import AuthService
from app.utils.verify import verify_token, require_role
from app.schemas.user import RegisterUser
from app.utils.logger import log_action

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])
auth_service = AuthService()


@router.post("/auth/register")
def register_user(data: RegisterUser):
    """
    Register a new user.
    
    Args:
        data: Registration data (email, password, display_name)
    
    Returns:
        User info with UID
    """
    try:
        user = auth_service.register_user(
            email=data.email,
            password=data.password,
            display_name=data.display_name,
            role="citizen"
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/me")
def get_current_user(user=Depends(verify_token)):
    """Get current logged-in user profile."""
    return {
        "uid": user["uid"],
        "email": user["email"],
        "display_name": user["display_name"],
        "role": user["role"],
        "area": user.get("area", {})
    }


@router.delete("/auth/delete")
def delete_current_user(user=Depends(verify_token)):
    """Delete current user account and profile."""
    try:
        auth_service.delete_user(user["uid"])
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/users/{uid}/role/{role}")
def set_user_role(
    uid: str,
    role: str,
    admin=Depends(require_role("admin"))
):
    """
    Set user role (admin only).
    
    Args:
        uid: Target user ID
        role: New role
        admin: Admin user context
    
    Returns:
        Success message
    """
    if role not in ["citizen", "responder", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    try:
        auth_service.update_user_role(admin["uid"], uid, role)
        return {"message": f"User role updated to {role}"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

