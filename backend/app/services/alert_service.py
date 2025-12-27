"""
Alert service - handles alert creation and management.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from app.firebase_config import get_db
from app.utils.logger import log_action

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert operations."""
    
    def __init__(self):
        self.db = get_db()
    
    def create_alert(
        self,
        user_id: str,
        title: str,
        message: str,
        level: str = "warning"
    ) -> Dict[str, Any]:
        """
        Create a new alert.
        
        Args:
            user_id: Creator user ID
            title: Alert title
            message: Alert message
            level: Alert level (info, warning, critical)
        
        Returns:
            Alert data with ID
        """
        try:
            alert_id = str(uuid.uuid4())
            
            alert_data = {
                "id": alert_id,
                "uid": user_id,
                "title": title,
                "message": message,
                "level": level,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            self.db.collection("alerts").document(alert_id).set(alert_data)
            
            log_action(
                logger,
                "alert_creation",
                "success",
                user_id=user_id,
                resource_id=alert_id,
                details={"level": level}
            )
            
            return alert_data
        except Exception as e:
            log_action(
                logger,
                "alert_creation",
                "failed",
                user_id=user_id,
                details={"error": str(e)}
            )
            raise
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
        
        Returns:
            Alert data or None
        """
        try:
            doc = self.db.collection("alerts").document(alert_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get alert {alert_id}: {e}")
            return None
    
    def get_active_alerts(self) -> list:
        """Get all active alerts."""
        try:
            alerts = []
            for doc in self.db.collection("alerts").where("status", "==", "active").stream():
                alert_data = doc.to_dict()
                alert_data["id"] = doc.id
                alerts.append(alert_data)
            return alerts
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def update_alert_status(
        self,
        alert_id: str,
        status: str
    ) -> bool:
        """
        Update alert status.
        
        Args:
            alert_id: Alert ID
            status: New status
        
        Returns:
            True if successful
        """
        try:
            self.db.collection("alerts").document(alert_id).update({
                "status": status,
                "updated_at": datetime.utcnow()
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to update alert {alert_id}: {e}")
            raise
