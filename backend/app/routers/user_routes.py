"""
User routes - handles user profile and area management.
"""
from fastapi import APIRouter, Depends, HTTPException
import logging
from app.firebase_config import get_db
from app.utils.verify import verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["Users"])


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
    radius_km: float = 20.0,
    user=Depends(verify_token)
):
    """
    Update user's area of interest.
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_km: Radius in kilometers
        user: Authenticated user
    
    Returns:
        Updated area info
    """
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

