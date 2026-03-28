"""
User routes - handles user profile and area management.
"""
from fastapi import APIRouter, Depends, HTTPException
import logging
from app.firebase_config import get_db, get_auth
from app.utils.verify import verify_token
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["Users"])
class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=6)

class ThemeUpdate(BaseModel):
    theme: str
    

@router.get("/me")
async def get_user_profile(user=Depends(verify_token)):
    """Get current user profile."""
    try:
        db = get_db()
        doc = db.collection("users").document(user["uid"]).get()
        
        if doc.exists:
            profile = doc.to_dict()
        else:
            profile = {
                "uid": user["uid"],
                "email": user["email"],
                "display_name": user["display_name"],
                "role": "citizen"
            }
        
        return profile
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.put("/me/area")
async def update_user_area(
    latitude: float,
    longitude: float,
    radius_km: float = 25.0,
    user=Depends(verify_token)
):
    try:
        if radius_km < 1 or radius_km > 100:
            raise HTTPException(status_code=400, detail="Radius must be between 1 and 100 km")
        
        db = get_db()
        area = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km
        }
        
        db.collection("users").document(user["uid"]).update({"area": area})
        
        return {"message": "Area updated", "area": area}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user area: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Delete user endpoint
@router.delete("/delete")
async def delete_user(user=Depends(verify_token)):
    try:
        db = get_db()
        db.collection("users").document(user["uid"]).delete()
        auth = get_auth()
        auth.delete_user(user["uid"])
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")
    
# Store user theme preference
@router.post("/theme")
async def set_user_theme(payload: ThemeUpdate, user=Depends(verify_token)):
    try:
        theme = payload.theme
        if theme not in ["light", "dark"]:
            raise HTTPException(status_code=400, detail="Theme must be 'light' or 'dark'")
        
        db = get_db()
        db.collection("users").document(user["uid"]).update({"theme": theme})
        
        return {"message": "Theme updated successfully", "theme": theme}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user theme: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
#Change password endpoint

@router.post("/change-password")
async def change_password(payload: ChangePasswordRequest, user=Depends(verify_token)):
    try:
        auth = get_auth()
        uid = user.get("uid")
        if not uid:
            raise HTTPException(status_code=400, detail="User ID not found in token")

        auth.update_user(uid, password=payload.new_password)
        logger.info(f"Password updated successfully for user {uid}")
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {e}")
        raise HTTPException(status_code=400, detail=str(e))