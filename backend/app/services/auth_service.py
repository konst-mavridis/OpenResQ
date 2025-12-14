"""
Authentication service - handles user registration, verification, and profile management.
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from app.firebase_config import get_db, get_auth
from app.utils.logger import log_action

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.db = get_db()
        self.auth = get_auth()
    
    def register_user(
        self,
        email: str,
        password: str,
        display_name: str,
        role: str = "citizen"
    ) -> Dict[str, Any]:
        """
        Register a new user with Firebase Authentication.
        
        Args:
            email: User email
            password: User password
            display_name: User display name
            role: User role (citizen, responder, admin)
        
        Returns:
            Dictionary with user UID and profile info
        """
        try:
            # Create Firebase auth user
            user = self.auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            # Create user profile in Firestore
            user_profile = {
                "uid": user.uid,
                "email": email,
                "display_name": display_name,
                "role": role,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "area": {  # Default area (Athens)
                    "latitude": 37.9838,
                    "longitude": 23.7275,
                    "radius_km": 20.0
                }
            }
            
            self.db.collection("users").document(user.uid).set(user_profile)
            
            log_action(
                logger,
                "user_registration",
                "success",
                user_id=user.uid,
                details={"email": email, "role": role}
            )
            
            return {
                "uid": user.uid,
                "email": email,
                "display_name": display_name,
                "role": role
            }
        except Exception as e:
            log_action(
                logger,
                "user_registration",
                "failed",
                details={"error": str(e), "email": email}
            )
            raise
    
    def get_user_profile(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore.
        
        Args:
            uid: User ID
        
        Returns:
            User profile dictionary or None if not found
        """
        try:
            doc = self.db.collection("users").document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile for {uid}: {e}")
            return None
    
    def create_or_get_user_profile(
        self,
        uid: str,
        email: str,
        display_name: str = "Anonymous"
    ) -> Dict[str, Any]:
        """
        Create user profile if not exists, otherwise return existing.
        
        Args:
            uid: User ID
            email: User email
            display_name: User display name
        
        Returns:
            User profile dictionary
        """
        profile = self.get_user_profile(uid)
        
        if profile:
            return profile
        
        # Create default profile
        profile = {
            "uid": uid,
            "email": email,
            "display_name": display_name,
            "role": "citizen",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "area": {
                "latitude": 37.9838,
                "longitude": 23.7275,
                "radius_km": 20.0
            }
        }
        
        self.db.collection("users").document(uid).set(profile)
        return profile
    
    def update_user_role(self, admin_uid: str, target_uid: str, role: str) -> bool:
        """
        Update user role (admin only).
        
        Args:
            admin_uid: Admin user ID
            target_uid: Target user ID
            role: New role
        
        Returns:
            True if successful
        """
        try:
            # Verify admin
            admin_doc = self.db.collection("users").document(admin_uid).get()
            if not admin_doc.exists or admin_doc.to_dict().get("role") != "admin":
                raise PermissionError("Only admins can update user roles")
            
            # Update role
            self.db.collection("users").document(target_uid).update({
                "role": role,
                "updated_at": datetime.utcnow()
            })
            
            log_action(
                logger,
                "role_change",
                "success",
                user_id=target_uid,
                details={"admin_id": admin_uid, "new_role": role}
            )
            
            return True
        except Exception as e:
            log_action(
                logger,
                "role_change",
                "failed",
                details={"error": str(e), "target_uid": target_uid, "admin_uid": admin_uid}
            )
            raise
    
    def delete_user(self, uid: str) -> bool:
        """
        Delete user account.
        
        Args:
            uid: User ID
        
        Returns:
            True if successful
        """
        try:
            # Delete from Firebase Auth
            self.auth.delete_user(uid)
            
            # Delete profile from Firestore
            self.db.collection("users").document(uid).delete()
            
            log_action(
                logger,
                "user_deletion",
                "success",
                user_id=uid
            )
            
            return True
        except Exception as e:
            log_action(
                logger,
                "user_deletion",
                "failed",
                user_id=uid,
                details={"error": str(e)}
            )
            raise
