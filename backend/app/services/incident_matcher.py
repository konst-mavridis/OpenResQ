from app.utils.geo import haversine_distance_km

def find_similar_reports(
    lat: float, lon: float, reports: list, radius_km: float = 0.1
) -> list:
    """
    Βρίσκει reports κοντά στη συντεταγμένη lat/lon εντός radius_km
    """
    similar = []
    for r in reports:
        r_lat = r.get("latitude")
        r_lon = r.get("longitude")
        if r_lat is None or r_lon is None:
            continue
        distance = haversine_distance_km(lat, lon, r_lat, r_lon)
        if distance <= radius_km:
            similar.append(r)
    return similar