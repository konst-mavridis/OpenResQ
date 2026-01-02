"""
Report service - handles report/incident creation, updates, and retrieval.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from app.firebase_config import get_db, get_fcm
from app.utils.geo import is_within_radius
from app.utils.logger import log_action
import math

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report/incident operations."""
    
    def __init__(self):
        self.db = get_db()
        self.fcm = get_fcm()

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    def create_report(
        self,
        user_id: str,
        title: str,
        description: str,
        event_type: str,
        severity: str,
        latitude: float,
        longitude: float,
        media: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new report/incident.
        
        Args:
            user_id: Creator user ID
            title: Report title
            description: Report description
            event_type: Type of event
            severity: Severity level (low, medium, high, critical)
            latitude: Latitude
            longitude: Longitude
            media: Optional media attachments
        
        Returns:
            Report data with ID
        """
        try:
            report_id = str(uuid.uuid4())
            
            report_data = {
                "id": report_id,
                "uid": user_id,
                "title": title,
                "description": description,
                "event_type": event_type,
                "severity": severity,
                "latitude": latitude,
                "longitude": longitude,
                "media": media or [],
                "status": "pending",
                "responder_notes": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            self.db.collection("reports").document(report_id).set(report_data)
            
            log_action(
                logger,
                "report_creation",
                "success",
                user_id=user_id,
                resource_id=report_id,
                details={"event_type": event_type, "severity": severity}
            )
            
            # Send FCM notification to responders
            try:
                message = {
                    "notification": {
                        "title": "New incident",
                        "body": f"{event_type} - {severity}"
                    },
                    "topic": "responders",
                    "data": {"report_id": report_id}
                }
                # Send would go here with FCM
            except Exception as e:
                logger.warning(f"Failed to send FCM notification: {e}")
            
            return report_data
        except Exception as e:
            log_action(
                logger,
                "report_creation",
                "failed",
                user_id=user_id,
                details={"error": str(e), "event_type": event_type}
            )
            raise
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Get report by ID.
        
        Args:
            report_id: Report ID
        
        Returns:
            Report data or None
        """
        try:
            doc = self.db.collection("reports").document(report_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get report {report_id}: {e}")
            return None
    
    def get_nearby_reports(
        self,
        user_id: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None
    ):
        print("🔥 get_nearby_reports START")
        
        try:
            # 1️⃣ user location
            if latitude is None or longitude is None:
                user_doc = self.db.collection("users").document(user_id).get()
                if user_doc.exists:
                    area = user_doc.to_dict().get("area", {})
                    latitude = float(area.get("latitude", 37.9838))
                    longitude = float(area.get("longitude", 23.7275))
                    radius_km = float(area.get("radius_km", 25))
                else:
                    latitude, longitude, radius_km = 37.9838, 23.7275, 25
            else:
                radius_km = radius_km or 25


            # 2️⃣ load reports
            docs = list(self.db.collection("reports").stream())

            reports = []

            for doc in docs:
                data = doc.to_dict()
                lat = data.get("latitude")
                lng = data.get("longitude")

                try:
                    lat = float(lat)
                    lng = float(lng)
                except:
                    continue

                distance = is_within_radius(
                    latitude, longitude,
                    lat, lng,
                    radius_km
                )


                if distance:
                    data["id"] = doc.id
                    reports.append(data)

            return reports

        except Exception as e:
            raise

    def update_report_status(
        self,
        report_id: str,
        status: str,
        updated_by: str
    ) -> bool:
        """
        Update report status.
        
        Args:
            report_id: Report ID
            status: New status
            updated_by: User ID making the update
        
        Returns:
            True if successful
        """
        try:
            self.db.collection("reports").document(report_id).update({
                "status": status,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            })
            
            log_action(
                logger,
                "report_update",
                "success",
                resource_id=report_id,
                details={"new_status": status, "updated_by": updated_by}
            )
            
            return True
        except Exception as e:
            log_action(
                logger,
                "report_update",
                "failed",
                resource_id=report_id,
                details={"error": str(e), "status": status}
            )
            raise
    
    def add_responder_note(
        self,
        report_id: str,
        responder_id: str,
        note: str
    ) -> bool:
        """
        Add a responder note to a report.
        
        Args:
            report_id: Report ID
            responder_id: Responder user ID
            note: Note text
        
        Returns:
            True if successful
        """
        try:
            note_data = {
                "responder_id": responder_id,
                "text": note,
                "timestamp": datetime.utcnow()
            }
            
            self.db.collection("reports").document(report_id).update({
                "responder_notes": self.db.collection("reports").document(report_id).get().to_dict().get("responder_notes", []) + [note_data],
                "updated_at": datetime.utcnow()
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to add responder note: {e}")
            raise
