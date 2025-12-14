<<<<<<< HEAD
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
=======
from fastapi import APIRouter, HTTPException, Depends
import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.schemas.user import RegisterUser, LoginUser
from app.utils.verify import verify_token
from app.utils.roles import require_roles
from app.firebase_config import db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------
# REGISTER
# ---------------------------
@router.post("/register")
def register_user(data: RegisterUser):
    try:
        user = auth.create_user(
            email=data.email,
            password=data.password,
            display_name=data.display_name
        )

        # Save user to Firestore
        db.collection("users").document(user.uid).set({
            "email": data.email,
            "display_name": data.display_name,
            "role": "citizen"
        })

        return {"message": "User created successfully.", "uid": user.uid}

>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


<<<<<<< HEAD
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
=======
# ---------------------------
# LOGIN (client must call Firebase REST API)
# ---------------------------
@router.post("/login")
def login_user(data: LoginUser):
    raise HTTPException(
        status_code=501,
        detail="Login is handled on client-side using Firebase Authentication REST API. "
               "Send ID token to backend for verification."
    )


# ---------------------------
# CHECK TOKEN
# ---------------------------
@router.get("/me")
def get_me(user: dict = Depends(verify_token)):
    uid = user["uid"]

    doc_ref = db.collection("users").document(uid).get()
    data = doc_ref.to_dict() if doc_ref.exists else None

    # If no user profile exists, return a default one
    if data is None:
        # Optional: auto-create a basic document
        default_data = {
            "role": "citizen",
            "display_name": user.get("name", "Anonymous")
        }
        db.collection("users").document(uid).set(default_data)
        data = default_data

    return {
        "uid": uid,
        "email": user.get("email"),
        "display_name": data.get("display_name", "Unknown"),
        "role": data.get("role", "citizen")
    }

# ---------------------------
# DELETE USER
# ---------------------------
@router.delete("/delete")
def delete_user(user=Depends(verify_token)):
    uid = user["uid"]

    try:
        auth.delete_user(uid)
        db.collection("users").document(uid).delete()
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

<<<<<<< HEAD

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

=======
@router.post("/set-role/{uid}/{role}")
def set_role(uid: str, role: str, user=Depends(verify_token)):
    # verify admin
    doc = db.collection("users").document(user['uid']).get()
    user_role = doc.to_dict().get("role")
    require_roles(user_role, ["admin"])

    # update role
    db.collection("users").document(uid).update({"role": role})
    return {"message": f"Role of {uid} updated to {role}"}
>>>>>>> 327748fd30086a4fd58a614cd888531a2bd9417a
