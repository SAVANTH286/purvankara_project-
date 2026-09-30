import math
from typing import Tuple, Dict, Any, Optional

# Earth's mean radius in kilometers
EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two geographic coordinates on Earth
    using the Haversine formula.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = EARTH_RADIUS_KM * c
    return round(distance, 2)


# Canonical Bengaluru micro-market coordinates lookup table
BENGALURU_COORDINATES = {
    "kanakapura road": (12.8718, 77.5458),
    "bagalur": (13.1332, 77.6749),
    "whitefield": (12.9698, 77.7500),
    "sarjapur road": (12.9081, 77.6844),
    "electronic city": (12.8399, 77.6770),
    "hebbal": (13.0358, 77.5970),
    "hebbal-bellary road": (13.0358, 77.5970),
    "thanisandra": (13.0569, 77.6341),
    "thanisandra-hennur": (13.0569, 77.6341),
    "koramangala": (12.9352, 77.6245),
    "indiranagar": (12.9784, 77.6408),
    "cbd": (12.9716, 77.6006),
    "cbd lavelle-mg-richmond": (12.9716, 77.6006),
    "jp nagar": (12.9063, 77.5857),
    "jp nagar-jayanagar-banashankari": (12.9063, 77.5857),
    "bannerghatta road": (12.8887, 77.5973),
    "btm layout": (12.9166, 77.6101),
    "devanahalli": (13.2483, 77.7126),
    "devanahalli-airport road": (13.2483, 77.7126),
    "jakkur-yelahanka": (13.0978, 77.5973),
    "yelahanka": (13.0978, 77.5973),
    "hoskote": (13.0699, 77.7981),
    "old airport road": (12.9592, 77.6974),
    "old airport road-marathahalli-kr puram": (12.9592, 77.6974),
    "old madras road-budigere cross": (13.0382, 77.7490),
    "orr marathahalli-sarjapur-hsr": (12.9121, 77.6446),
    "hosur road-begur": (12.8787, 77.6322),
    "attibele-chandapur": (12.7801, 77.7712),
    "malleshwaram-rajajinagar-yeshwanthpur": (13.0033, 77.5645),
    "tumkur road-vijayanagar": (12.9719, 77.5304),
    "mysore road-uttarahalli-magadi road": (12.9344, 77.5147),
    "off-central": (12.9982, 77.6046)
}


def resolve_coordinates(micro_market_name: str, location_hint: Optional[str] = None) -> Tuple[float, float]:
    """
    Resolves validated real geographic coordinates for a micro-market or location string in Bengaluru.
    """
    mm_lower = (micro_market_name or "").strip().lower()
    loc_lower = (location_hint or "").strip().lower()

    # Direct match on micro-market
    for key, coords in BENGALURU_COORDINATES.items():
        if key in mm_lower or mm_lower in key:
            return coords

    # Match on location hint
    for key, coords in BENGALURU_COORDINATES.items():
        if key in loc_lower or loc_lower in key:
            return coords

    # Default to Bengaluru city center (Vidhana Soudha / MG Road)
    return (12.9716, 77.5946)


def find_nearest_micromarket(latitude: float, longitude: float) -> Tuple[str, float]:
    """
    Given any arbitrary latitude/longitude in Bengaluru, finds the nearest canonical
    micro-market and returns (micro_market_name, distance_km).
    """
    nearest_name = "Bengaluru Urban"
    min_dist = 9999.0

    for key, coords in BENGALURU_COORDINATES.items():
        dist = haversine_distance_km(latitude, longitude, coords[0], coords[1])
        if dist < min_dist:
            min_dist = dist
            nearest_name = key.title()

    return nearest_name, round(min_dist, 2)


def is_valid_bengaluru_coordinates(latitude: float, longitude: float) -> bool:
    """
    Checks if coordinates lie within the broader Bengaluru metropolitan region
    (approximately lat: 12.5 to 13.6, lon: 77.1 to 78.1).
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        return 12.5 <= lat <= 13.6 and 77.1 <= lon <= 78.1
    except (ValueError, TypeError):
        return False

