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
from app.utils.email import send_reset_email
from app.schemas.reset import ResetEmailRequest, ResetPasswordRequest, OTPRequest, OTPVerify
import random
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from firebase_admin import auth as fb_auth
from firebase_admin import firestore
from app.firebase_config import db
from app.utils.email import send_email

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

@router.post("/send-reset-email")
async def send_reset_email_route(body: ResetEmailRequest):
    email = body.email.lower()

    # 1. check if user exists in Firebase Auth
    try:
        user = fb_auth.get_user_by_email(email)
    except fb_auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Email not found")

    # 2. create token doc in Firestore
    token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    db.collection("password_resets").document(token).set({
        "email": email,
        "uid": user.uid,
        "expires_at": expires_at.isoformat(),
    })

    # 3. build reset link (web ή deep link)
    reset_link = f"https://openresq.app/reset-password?token={token}"

    # 4. send email
    try:
        send_reset_email(email, reset_link)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {e}")

    return {"success": True}


@router.post("/reset-password")
async def reset_password_route(body: ResetPasswordRequest):
    token = body.token
    new_password = body.new_password

    doc_ref = db.collection("password_resets").document(token)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=400, detail="Invalid token")

    data = doc.to_dict()
    expires_at = datetime.fromisoformat(data["expires_at"])

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Token expired")

    email = data["email"]
    uid = data["uid"]

    # update password in Firebase Auth
    try:
        fb_auth.update_user(uid, password=new_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update password: {e}")

    # delete token
    doc_ref.delete()

    return {"success": True}

@router.post("/auth/send-otp")
async def send_otp(body: OTPRequest):
    email = body.email.lower()

    try:
        user = fb_auth.get_user_by_email(email)
    except:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.collection("email_verification").document(user.uid).set({
        "email": email,
        "otp": otp,
        "expires_at": expires.isoformat(),
        "verified": False,
        "attempts": 0,
        "last_sent": datetime.now(timezone.utc).isoformat()
    })

    html = f"""
    <h2>Your OpenResQ Verification Code</h2>
    <h1>{otp}</h1>
    <p>This code expires in 10 minutes.</p>
    """

    send_email(email, "OpenResQ Email Verification", html)

    return {"success": True}

@router.post("/auth/verify-otp")
async def verify_otp(body: OTPVerify):
    email = body.email.lower()
    otp = body.otp

    try:
        user = fb_auth.get_user_by_email(email)
    except:
        raise HTTPException(status_code=404, detail="Email not found")

    doc_ref = db.collection("email_verification").document(user.uid)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=400, detail="OTP not found")

    data = doc.to_dict()

    if data["attempts"] >= 5:
        raise HTTPException(status_code=403, detail="Too many attempts. Blocked.")

    if datetime.now(timezone.utc) > datetime.fromisoformat(data["expires_at"]):
        raise HTTPException(status_code=400, detail="OTP expired")

    if data["otp"] != otp:
        doc_ref.update({"attempts": data["attempts"] + 1})
        raise HTTPException(status_code=400, detail="Invalid OTP")

    doc_ref.update({"verified": True})

    return {"success": True}

@router.post("/auth/resend-otp")
async def resend_otp(body: OTPRequest):
    email = body.email.lower()

    try:
        user = fb_auth.get_user_by_email(email)
    except:
        raise HTTPException(status_code=404, detail="Email not found")

    doc_ref = db.collection("email_verification").document(user.uid)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        last_sent = datetime.fromisoformat(data["last_sent"])
        if datetime.now(timezone.utc) < last_sent + timedelta(seconds=60):
            raise HTTPException(status_code=429, detail="Wait 60 seconds before resending")

    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    doc_ref.set({
        "email": email,
        "otp": otp,
        "expires_at": expires.isoformat(),
        "verified": False,
        "attempts": 0,
        "last_sent": datetime.now(timezone.utc).isoformat()
    })

    html = f"""
    <h2>Your New OpenResQ Verification Code</h2>
    <h1>{otp}</h1>
    <p>This code expires in 10 minutes.</p>
    """

    send_email(email, "OpenResQ Email Verification", html)

    return {"success": True}
