import math
def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def is_within_radius(center_lat, center_lng, lat, lng, radius_km):
    if center_lat is None or center_lng is None or radius_km is None:
        return True
    return haversine_distance_km(center_lat, center_lng, lat, lng) <= radius_km

