from fastapi import APIRouter
from app.services.weather_services import fetch_weather
from app.services.weather_risk import calculate_weather_risk
from app.services.historical_service import fetch_historical_reports
from app.services.report_service import ReportService

router = APIRouter(prefix="/risk", tags=["Risk"])

@router.get("/area")
def get_area_risk(user_id: str, lat: float, lng: float, radius_km: float = 20):
    # Weather
    weather = fetch_weather(lat, lng)
    weather_risk = calculate_weather_risk(weather)

    # Active incidents
    report_service = ReportService()
    active_incidents = report_service.get_nearby_reports(
        user_id=user_id,
        latitude=lat,
        longitude=lng,
        radius_km=radius_km
    )

    # Historical incidents (15 years)
    historical = fetch_historical_reports(lat, lng, radius_km, years=15)

    # Simple historical risk (placeholder)
    historical_risk = min(100, len(historical) * 0.5)

    # Combine
    total_risk = (
        weather_risk * 0.35 +
        historical_risk * 0.25 +
        len(active_incidents) * 0.4
    )

    risk_level = (
        "high" if total_risk > 70 else
        "medium" if total_risk > 40 else
        "low"
    )

    return {
        "risk_score": total_risk,
        "risk_level": risk_level,
        "weather_risk": weather_risk,
        "active_incidents": len(active_incidents),
        "historical_incidents": len(historical),
    }
