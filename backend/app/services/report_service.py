"""
Report service - handles report/incident creation, updates, and retrieval.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from firebase_admin import storage
from app.firebase_config import get_db, get_fcm
from app.utils.geo import is_within_radius
from app.utils.logger import log_action
import math
import requests
from io import BytesIO
from openai import OpenAI
import json
import base64


logger = logging.getLogger(__name__)
client = OpenAI()

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
    
    
    def upload_image_to_firebase(self, file_url: str, folder: str = "reports") -> str:
        """
        Κατεβάζει την εικόνα από το URL και την ανεβάζει στο Firebase Storage.
        Επιστρέφει το δημόσιο URL.

        Args:
            file_url: URL εικόνας
            folder: φάκελος στο storage

        Returns:
            public URL της εικόνας
        """
        try:
            # Κατέβασε την εικόνα
            response = requests.get(file_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {file_url}")
            
            blob_name = f"{folder}/{uuid.uuid4()}.jpg"
            bucket = storage.bucket()
            blob = bucket.blob(blob_name)
            
            blob.upload_from_file(BytesIO(response.content), content_type="image/jpeg")
            blob.make_public()  # ώστε να πάρουμε public URL
            return blob.public_url
        except Exception as e:
            raise Exception(f"Firebase upload failed: {str(e)}")
    def run_ai_analysis(self, image_url: str) -> dict:
        """
        OpenAI Vision με το νέο Responses API (όπως στα docs).
        Επιστρέφει: {"fire": bool, "confidence": float}
        """

        try:
            print("\n========== [AI DEBUG START] ==========")
            print(f"[AI] Vision URL: {image_url}")

            # ---- 1) Κατέβασμα εικόνας ----
            resp = requests.get(image_url, timeout=20)
            resp.raise_for_status()
            img_bytes = resp.content
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            print(f"[AI] Download OK — size: {len(img_bytes)/1024:.2f} KB")

            # ---- 2) Prompt ----
            prompt = """
            Analyze this image carefully.

            Your task:
            - Determine if there is visible FIRE or heavy SMOKE.
            - Ignore fog, dust, sunset, headlights, or reflections.
            - If you see real flames OR dense burning smoke, mark fire=true.

            Return ONLY valid JSON like:
            {
            "fire": true/false,
            "confidence": 0.0-1.0
            }
            """

            # ---- 3) Κλήση OpenAI (όπως στα docs) ----
            response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{img_b64}",
                            },
                        ],
                    }
                ],
            )

            # ---- 4) Πάρε καθαρό κείμενο ----
            text = response.output_text.strip()
            print("\n[AI] RAW OpenAI response:")
            print(text)

            # ---- 5) Μετέτρεψε σε JSON ----
            try:
                result = json.loads(text)
                fire = bool(result.get("fire", False))
                confidence = float(result.get("confidence", 0.0))

                print(f"[AI] FINAL RESULT -> fire={fire}, confidence={confidence}")
                print("========== [AI DEBUG END] ==========\n")

                return {"fire": fire, "confidence": confidence}

            except json.JSONDecodeError as je:
                print("[AI] JSON PARSE ERROR:", je)
                print("Returning defaults")
                return {"fire": False, "confidence": 0.0}

        except Exception as e:
            print("\n[AI] CRITICAL ERROR:", e)
            print("========== [AI DEBUG END] ==========\n")
            return {"fire": False, "confidence": 0.0}


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
        ai_score: Optional[float] = 0.0,
        ai_fire_detected: Optional[bool] = False
    ):
        try:
            uploaded_media = []
            if media:
                for i, m in enumerate(media):
                    if "file_path" in m:
                        url = self.upload_image_to_firebase(m["file_path"])
                        uploaded_media.append({"url": url, "type": "image"})
                    elif "url" in m:
                        uploaded_media.append({"url": m["url"], "type": m.get("type", "image")})

            report_data = {
                "id": str(uuid.uuid4()),
                "uid": user_id,
                "title": title,
                "description": description,
                "event_type": event_type,
                "severity": severity,
                "latitude": latitude,
                "longitude": longitude,
                "media": uploaded_media,
                "ai_score": ai_score,
                "ai_fire_detected": ai_fire_detected,
                "status": "pending",          # default
                "votes": {},
                "confidence": 0.5,            # ξεκινάει στη μέση
                "needs_admin_review": False,  # ← ΝΕΟ
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            self.db.collection("reports").document(report_data["id"]).set(report_data)
            print(f"[DEBUG] Created report: {report_data}")
            return report_data

        except Exception as e:
            print(f"[ERROR] Failed to create report: {e}")
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
    def get_recent_reports(self, hours):
        """
        Επιστρέφει όλα τα reports που δημιουργήθηκαν τις τελευταίες `hours` ώρες.
        """
        now = datetime.utcnow()
        past_time = now - timedelta(hours=hours)

        reports = []
        query = self.db.collection("reports").where("deleted", "!=", True).stream()
        for r in query:
            d = r.to_dict()
            created_at = d.get("created_at")
            if created_at and created_at >= past_time:
                d["id"] = r.id
                reports.append(d)
        return reports
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

    def update_report(self, report_id: str, updates: dict) -> Dict[str, Any]:
        """
        Update any fields in a report.

        Args:
            report_id: Report ID
            updates: Dict of fields to update

        Returns:
            Updated report dict
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            self.db.collection("reports").document(report_id).update(updates)
            doc = self.db.collection("reports").document(report_id).get()
            return doc.to_dict()
        except Exception as e:
            logger.error(f"Failed to update report {report_id}: {e}")
            raise
