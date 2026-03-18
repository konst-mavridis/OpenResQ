from google.cloud import firestore
from datetime import datetime, timedelta
import math
from app.firebase_config import get_db

db = get_db()

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )
    return R * 2 * math.asin(math.sqrt(a))

def fetch_historical_reports(lat: float, lng: float, radius_km: float = 20, years: int = 15):
    since = datetime.utcnow() - timedelta(days=365 * years)

    docs = db.collection("historical_reports") \
        .where("created_at", ">=", since) \
        .stream()

    results = []
    for doc in docs:
        d = doc.to_dict()
        dist = haversine_km(lat, lng, d["latitude"], d["longitude"])
        if dist <= radius_km:
            results.append({
                "lat": d["latitude"],
                "lng": d["longitude"],
                "type": d.get("type", "unknown"),
                "created_at": d["created_at"],
                "status": d.get("status", "unknown"),
                "distance_km": dist,
            })

    return results
