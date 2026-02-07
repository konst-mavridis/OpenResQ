from datetime import datetime, timedelta
from firebase_admin import firestore
import asyncio
import logging
from app.services.report_service import ReportService
from app.utils.ws_manager import ws_manager
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.db = firestore.client()
        self.report_service = ReportService()

    def overview(self, user_id, latitude: float, longitude: float, radius_km: float):
        reports = self.report_service.get_nearby_reports(user_id, latitude, longitude, radius_km)
        users = self.db.collection("users").stream()
        alerts = self.db.collection("alerts").stream()

        total_reports = 0
        verified_reports = 0
        total_votes = 0

        for r in reports:
            data = r
            total_reports += 1
            total_votes += len(data.get("votes", {}))
            if data.get("confidence", 0) >= 0.7:
                verified_reports += 1

        total_users = sum(1 for _ in users)
        total_alerts = sum(1 for _ in alerts)

        return {
            "reports": {
                "total": total_reports,
                "verified": verified_reports,
                "pending": total_reports - verified_reports
            },
            "votes": {
                "total": total_votes
            },
            "users": {
                "total": total_users
            },
            "alerts": {
                "total": total_alerts
            }
        }

    def reports_last_24h(self, user_id, latitude: float, longitude: float, radius_km: float):
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        all_reports = self.report_service.get_nearby_reports(user_id, latitude, longitude, radius_km)

    
        reports = (r for r in all_reports if r.get("created_at") and r.get("created_at") >= since)

        return sum(1 for _ in all_reports)

    def heatmap_by_hazard(self, hazard: str, user_id, latitude: float, longitude: float, radius_km: float):
        all_reports = self.report_service.get_nearby_reports(user_id, latitude, longitude, radius_km)

        reports = (r for r in all_reports if r.get("hazard_type") == hazard)
        points = []

        for r in reports:
            data = r
            loc = data.get("location")
            if not loc:
                continue

            points.append({
                "lat": loc["lat"],
                "lng": loc["lng"],
                "weight": data.get("confidence", 0.5)
            })

        return points


    def top_hazards(self, limit=5, user_id=None, latitude: float=None, longitude: float=None, radius_km: float=None):
        all_reports = self.report_service.get_nearby_reports(user_id, latitude, longitude, radius_km)

        counter = {}

        for r in all_reports:
            hazard = r.get("hazard_type")
            if hazard:
                counter[hazard] = counter.get(hazard, 0) + 1

        return sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]

    async def broadcast_overview(self, user_id, latitude: float, longitude: float, radius_km: float):
        """Broadcast analytics overview to all admins via WebSocket."""
        data = self.overview(user_id, latitude, longitude, radius_km)
        await ws_manager.broadcast(
            {
                "type": "analytics_overview",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )

    async def broadcast_hazards(self):
        """Broadcast top hazards to all admins via WebSocket."""
        hazards = self.top_hazards()
        await ws_manager.broadcast(
            {
                "type": "analytics_hazards",
                "data": {"hazards": hazards},
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )

    async def broadcast_heatmap(self, hazard: str):
        """Broadcast heatmap data to all admins via WebSocket."""
        points = self.heatmap_by_hazard(hazard)
        await ws_manager.broadcast(
            {
                "type": "analytics_heatmap",
                "data": {
                    "hazard": hazard,
                    "points": points
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            filter_by_role="admin"
        )
