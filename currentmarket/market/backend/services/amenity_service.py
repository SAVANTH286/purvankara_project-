import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from backend.services.geospatial_service import (
    haversine_distance_km,
    find_nearest_micromarket,
    is_valid_bengaluru_coordinates
)

# Overpass API mirrors for high availability and failover
OVERPASS_SERVERS = [
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

CACHE_FILE_PATH = os.path.join(os.path.dirname(__file__), ".poi_cache.json")


class AmenityService:
    _instance = None

    def __init__(self):
        self.memory_cache: Dict[str, Any] = {}
        self._load_disk_cache()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AmenityService()
        return cls._instance

    def _load_disk_cache(self):
        if os.path.exists(CACHE_FILE_PATH):
            try:
                with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                    self.memory_cache = json.load(f)
            except Exception:
                self.memory_cache = {}

    def _save_disk_cache(self):
        try:
            with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.memory_cache, f, ensure_ascii=False)
        except Exception:
            pass

    def get_amenities_within_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Retrieves real, verified points of interest within radius_km (default: 5.0 km = 5000 m)
        from EXACTLY the selected latitude/longitude using OpenStreetMap / Overpass API.
        Calculates exact Haversine distances, sorts by distance, and calculates category & subcategory counts.
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
        except (ValueError, TypeError):
            return {
                "status": "error",
                "error": "Invalid coordinate format",
                "center": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km,
                "radius_meters": int(radius_km * 1000),
                "description": f"{int(radius_km)} KM radius from selected location",
                "total_count": "Data Unavailable",
                "counts_by_category": {cat: "Data Unavailable" for cat in [
                    "Transport", "Education", "Healthcare", "Commercial", "Employment", "Recreation", "Other Amenities"
                ]},
                "sub_counts": {k: "Data Unavailable" for k in [
                    "metro_stations", "bus_stops", "railway_stations", "schools", "colleges",
                    "hospitals", "clinics", "malls_commercial", "supermarkets", "it_tech_parks",
                    "employment_centres", "parks_recreation", "other_amenities"
                ]},
                "nearest_facilities": {k: "Data Unavailable" for k in [
                    "nearest_metro", "nearest_school", "nearest_hospital",
                    "nearest_commercial", "nearest_it_park", "nearest_bus_stop"
                ]},
                "amenities": [],
                "source": "OpenStreetMap"
            }

        # Check bounds (Greater Bengaluru)
        if not is_valid_bengaluru_coordinates(lat, lon):
            # Still attempt or return descriptive message
            pass

        cache_key = f"{round(lat, 3)}_{round(lon, 3)}_{round(radius_km, 1)}"
        if cache_key in self.memory_cache:
            cached_result = self.memory_cache[cache_key]
            # Recalculate distance to exact selected coordinates in case of small rounding delta
            return self._recalculate_exact_distances(cached_result, lat, lon)

        radius_m = int(radius_km * 1000)
        elements, error_msg = self._query_overpass(lat, lon, radius_m)

        if error_msg is not None:
            # Query failed: do NOT convert error to 0! Return "Data Unavailable"
            return {
                "status": "error",
                "error": error_msg,
                "center": {"latitude": lat, "longitude": lon},
                "radius_km": radius_km,
                "radius_meters": radius_m,
                "description": f"{int(radius_km)} KM radius from selected location",
                "total_count": "Data Unavailable",
                "counts_by_category": {cat: "Data Unavailable" for cat in [
                    "Transport", "Education", "Healthcare", "Commercial", "Employment", "Recreation", "Other Amenities"
                ]},
                "sub_counts": {k: "Data Unavailable" for k in [
                    "metro_stations", "bus_stops", "railway_stations", "schools", "colleges",
                    "hospitals", "clinics", "malls_commercial", "supermarkets", "it_tech_parks",
                    "employment_centres", "parks_recreation", "other_amenities"
                ]},
                "nearest_facilities": {k: "Data Unavailable" for k in [
                    "nearest_metro", "nearest_school", "nearest_hospital",
                    "nearest_commercial", "nearest_it_park", "nearest_bus_stop"
                ]},
                "amenities": [],
                "source": "OpenStreetMap"
            }

        # Process and classify raw OSM elements
        amenities = []
        seen_keys = set()

        for el in elements:
            poi = self._classify_element(el, lat, lon, radius_km)
            if poi:
                # Deduplicate by name and approx coordinates
                dedup_key = (poi["name"].lower().strip(), round(poi["latitude"], 3), round(poi["longitude"], 3))
                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    amenities.append(poi)

        # Sort all amenities by distance ascending
        amenities.sort(key=lambda x: x["distance_from_selected_point"])

        # Category Counts
        counts_by_category = {
            "Transport": 0,
            "Education": 0,
            "Healthcare": 0,
            "Commercial": 0,
            "Employment": 0,
            "Recreation": 0,
            "Other Amenities": 0
        }
        for a in amenities:
            cat = a["category"]
            counts_by_category[cat] = counts_by_category.get(cat, 0) + 1

        # Detailed Sub-category counts (exact requested structure)
        sub_counts = {
            "metro_stations": sum(1 for p in amenities if p["subcategory"] == "Metro Station"),
            "bus_stops": sum(1 for p in amenities if p["subcategory"] in ("Bus Stop", "Bus Terminal")),
            "railway_stations": sum(1 for p in amenities if p["subcategory"] == "Railway Station"),
            "schools": sum(1 for p in amenities if p["subcategory"] == "School"),
            "colleges": sum(1 for p in amenities if p["subcategory"] in ("College", "University")),
            "hospitals": sum(1 for p in amenities if p["subcategory"] == "Hospital"),
            "clinics": sum(1 for p in amenities if p["subcategory"] in ("Clinic", "Pharmacy", "Diagnostic Centre")),
            "malls_commercial": sum(1 for p in amenities if p["subcategory"] == "Mall / Shopping Centre"),
            "supermarkets": sum(1 for p in amenities if p["subcategory"] in ("Supermarket", "Marketplace")),
            "it_tech_parks": sum(1 for p in amenities if p["subcategory"] == "IT / Tech Park"),
            "employment_centres": sum(1 for p in amenities if p["category"] == "Employment"),
            "parks_recreation": sum(1 for p in amenities if p["category"] == "Recreation"),
            "other_amenities": sum(1 for p in amenities if p["category"] == "Other Amenities")
        }

        # Nearest facilities identification
        def _get_nearest(filter_fn):
            for a in amenities:
                if filter_fn(a):
                    return {
                        "name": a["name"],
                        "subcategory": a["subcategory"],
                        "distance_km": a["distance_km"],
                        "latitude": a["latitude"],
                        "longitude": a["longitude"]
                    }
            return None

        nearest_facilities = {
            "nearest_metro": _get_nearest(lambda a: a["subcategory"] == "Metro Station"),
            "nearest_school": _get_nearest(lambda a: a["subcategory"] == "School"),
            "nearest_hospital": _get_nearest(lambda a: a["subcategory"] == "Hospital"),
            "nearest_commercial": _get_nearest(lambda a: a["category"] == "Commercial"),
            "nearest_it_park": _get_nearest(lambda a: a["category"] == "Employment"),
            "nearest_bus_stop": _get_nearest(lambda a: a["subcategory"] in ("Bus Stop", "Bus Terminal"))
        }

        nearest_mm_name, nearest_mm_dist = find_nearest_micromarket(lat, lon)

        result = {
            "status": "available",
            "center": {
                "latitude": round(lat, 5),
                "longitude": round(lon, 5)
            },
            "radius_km": radius_km,
            "radius_meters": radius_m,
            "description": f"{int(radius_km)} KM radius from selected location",
            "nearest_micromarket": {
                "name": nearest_mm_name,
                "distance_km": nearest_mm_dist
            },
            "total_count": len(amenities),
            "counts_by_category": counts_by_category,
            "sub_counts": sub_counts,
            "nearest_facilities": nearest_facilities,
            "amenities": amenities,
            "source": "OpenStreetMap",
            "disclaimer": f"Showing {len(amenities)} real available mapped amenities from OpenStreetMap within 5 km.",
            "limitations": [
                "Amenities reflect points of interest mapped in OpenStreetMap within 5 km of the selected point.",
                "Distances are calculated as direct great-circle (Haversine) lines from exact selected coordinates."
            ]
        }

        # Cache result
        self.memory_cache[cache_key] = result
        self._save_disk_cache()

        return result

    def _query_overpass(self, lat: float, lon: float, radius_m: int) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Executes an optimized Overpass QL query across available servers with failover.
        Retrieves transport, education, healthcare, commercial, employment, recreation, and other amenities.
        """
        q = f"""[out:json][timeout:10];
        (
          // 1. METRO & RAILWAY
          node["railway"="station"](around:{radius_m},{lat},{lon});
          way["railway"="station"](around:{radius_m},{lat},{lon});
          node["station"="subway"](around:{radius_m},{lat},{lon});
          way["station"="subway"](around:{radius_m},{lat},{lon});
          node["railway"="subway_entrance"](around:{radius_m},{lat},{lon});
          node["railway"="stop"](around:{radius_m},{lat},{lon});
          node["railway"="halt"](around:{radius_m},{lat},{lon});

          // 2. EDUCATION
          node["amenity"="school"](around:{radius_m},{lat},{lon});
          way["amenity"="school"](around:{radius_m},{lat},{lon});
          node["amenity"="college"](around:{radius_m},{lat},{lon});
          way["amenity"="college"](around:{radius_m},{lat},{lon});
          node["amenity"="university"](around:{radius_m},{lat},{lon});
          way["amenity"="university"](around:{radius_m},{lat},{lon});

          // 3. HEALTHCARE
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="clinic"](around:{radius_m},{lat},{lon});
          way["amenity"="clinic"](around:{radius_m},{lat},{lon});
          node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
          node["amenity"="doctors"](around:{radius_m},{lat},{lon});

          // 4. COMMERCIAL
          node["shop"="mall"](around:{radius_m},{lat},{lon});
          way["shop"="mall"](around:{radius_m},{lat},{lon});
          node["shop"="supermarket"](around:{radius_m},{lat},{lon});
          way["shop"="supermarket"](around:{radius_m},{lat},{lon});
          node["amenity"="marketplace"](around:{radius_m},{lat},{lon});

          // 5. EMPLOYMENT
          node["office"="company"](around:{radius_m},{lat},{lon});
          node["office"="it"](around:{radius_m},{lat},{lon});
          node["landuse"="commercial"](around:{radius_m},{lat},{lon});

          // 6. RECREATION
          node["leisure"="park"](around:{radius_m},{lat},{lon});
          way["leisure"="park"](around:{radius_m},{lat},{lon});
          node["leisure"="playground"](around:{radius_m},{lat},{lon});
          node["leisure"="sports_centre"](around:{radius_m},{lat},{lon});

          // 7. BUS STOPS & TERMINALS
          node["highway"="bus_stop"](around:{radius_m},{lat},{lon});
          node["amenity"="bus_station"](around:{radius_m},{lat},{lon});

          // 8. OTHER AMENITIES
          node["amenity"="bank"](around:{radius_m},{lat},{lon});
          node["amenity"="atm"](around:{radius_m},{lat},{lon});
          node["amenity"="fuel"](around:{radius_m},{lat},{lon});
          node["amenity"="police"](around:{radius_m},{lat},{lon});
          node["amenity"="place_of_worship"](around:{radius_m},{lat},{lon});
        );
        out center 350;"""

        headers = {
            "User-Agent": "PuravankaraDSS/1.0 (contact@puravankara.com)",
            "Accept": "application/json"
        }

        last_error = None
        for server in OVERPASS_SERVERS:
            try:
                resp = requests.get(server, params={"data": q}, headers=headers, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    elements = data.get("elements", [])
                    return elements, None
                else:
                    last_error = f"Server {server} returned HTTP {resp.status_code}"
            except Exception as e:
                last_error = f"Server {server} error: {str(e)}"

        return [], f"Overpass API query failed: {last_error}"

    def _classify_element(
        self,
        elem: Dict[str, Any],
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> Optional[Dict[str, Any]]:
        """
        Classifies an OSM node or way into one of the 7 core categories and subcategories,
        and calculates its exact Haversine distance from the center.
        """
        tags = elem.get("tags", {})
        lat = elem.get("lat") or elem.get("center", {}).get("lat")
        lon = elem.get("lon") or elem.get("center", {}).get("lon")

        if not lat or not lon:
            return None

        dist = haversine_distance_km(center_lat, center_lon, lat, lon)
        if dist > radius_km:
            return None

        name = tags.get("name") or tags.get("name:en") or tags.get("operator") or tags.get("brand")
        category = None
        subcategory = None

        name_lower = (name or "").lower()
        net = tags.get("network", "").lower()
        op = tags.get("operator", "").lower()

        # 1. Transport — Metro
        is_metro = (
            "namma metro" in net or "bmrcl" in net or "namma metro" in op or "bmrcl" in op or
            tags.get("station") == "subway" or tags.get("subway") == "yes" or
            tags.get("railway") == "subway_entrance" or
            "metro station" in name_lower or "metro" in name_lower
        )
        if is_metro:
            category = "Transport"
            subcategory = "Metro Station"

        # Transport — Heavy Railway
        elif tags.get("railway") in ("station", "halt") and not is_metro:
            category = "Transport"
            subcategory = "Railway Station"

        # Transport — Bus
        elif tags.get("highway") == "bus_stop" or tags.get("amenity") == "bus_station":
            category = "Transport"
            subcategory = "Bus Stop" if tags.get("highway") == "bus_stop" else "Bus Terminal"

        # Transport — Airport
        elif tags.get("aeroway") == "aerodrome":
            category = "Transport"
            subcategory = "Airport / Terminal"

        # 2. Education
        elif tags.get("amenity") == "school":
            category = "Education"
            subcategory = "School"
        elif tags.get("amenity") == "college":
            category = "Education"
            subcategory = "College"
        elif tags.get("amenity") == "university":
            category = "Education"
            subcategory = "University"

        # 3. Healthcare
        elif tags.get("amenity") == "hospital":
            category = "Healthcare"
            subcategory = "Hospital"
        elif tags.get("amenity") in ("clinic", "doctors"):
            category = "Healthcare"
            subcategory = "Clinic"
        elif tags.get("amenity") == "pharmacy":
            category = "Healthcare"
            subcategory = "Pharmacy"

        # 4. Commercial
        elif tags.get("shop") == "mall" or "mall" in name_lower:
            category = "Commercial"
            subcategory = "Mall / Shopping Centre"
        elif tags.get("shop") == "supermarket":
            category = "Commercial"
            subcategory = "Supermarket"
        elif tags.get("amenity") == "marketplace":
            category = "Commercial"
            subcategory = "Marketplace"

        # 5. Employment
        elif tags.get("office") in ("company", "it") or tags.get("landuse") == "commercial":
            category = "Employment"
            if "tech park" in name_lower or "it park" in name_lower or tags.get("office") == "it":
                subcategory = "IT / Tech Park"
            else:
                subcategory = "Employment Centre"

        # 6. Recreation
        elif tags.get("leisure") == "park":
            category = "Recreation"
            subcategory = "Park"
        elif tags.get("leisure") == "playground":
            category = "Recreation"
            subcategory = "Playground"
        elif tags.get("leisure") in ("sports_centre", "pitch"):
            category = "Recreation"
            subcategory = "Sports Facility"

        # 7. Other Amenities
        elif tags.get("amenity") == "bank":
            category = "Other Amenities"
            subcategory = "Bank"
        elif tags.get("amenity") == "atm":
            category = "Other Amenities"
            subcategory = "ATM"
        elif tags.get("amenity") in ("restaurant", "cafe"):
            category = "Other Amenities"
            subcategory = "Restaurant / Cafe"
        elif tags.get("amenity") == "fuel":
            category = "Other Amenities"
            subcategory = "Fuel Station"
        elif tags.get("amenity") == "police":
            category = "Other Amenities"
            subcategory = "Police Station"
        elif tags.get("amenity") == "place_of_worship":
            category = "Other Amenities"
            subcategory = "Place of Worship"

        if not category:
            return None

        if not name:
            name = f"{subcategory} ({tags.get('brand') or 'Public Facility'})"

        return {
            "name": name,
            "category": category,
            "subcategory": subcategory,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "distance_from_selected_point": dist,
            "distance_km": dist,
            "source": "OpenStreetMap"
        }

    def _recalculate_exact_distances(self, cached_result: Dict[str, Any], new_lat: float, new_lon: float) -> Dict[str, Any]:
        """
        Recalculates exact distances for cached POIs when coordinates have tiny sub-grid deltas.
        """
        if cached_result.get("status") != "available":
            return cached_result

        result = dict(cached_result)
        result["center"] = {"latitude": round(new_lat, 5), "longitude": round(new_lon, 5)}
        amenities = []

        for a in cached_result.get("amenities", []):
            item = dict(a)
            dist = haversine_distance_km(new_lat, new_lon, item["latitude"], item["longitude"])
            if dist <= result.get("radius_km", 5.0):
                item["distance_from_selected_point"] = dist
                item["distance_km"] = dist
                amenities.append(item)

        amenities.sort(key=lambda x: x["distance_from_selected_point"])
        result["amenities"] = amenities
        result["total_count"] = len(amenities)

        # Category Counts
        counts_by_category = {
            "Transport": 0,
            "Education": 0,
            "Healthcare": 0,
            "Commercial": 0,
            "Employment": 0,
            "Recreation": 0,
            "Other Amenities": 0
        }
        for a in amenities:
            cat = a.get("category")
            if cat in counts_by_category:
                counts_by_category[cat] += 1
            else:
                counts_by_category[cat] = 1
        result["counts_by_category"] = counts_by_category

        # Detailed Sub-category counts
        result["sub_counts"] = {
            "metro_stations": sum(1 for p in amenities if p.get("subcategory") == "Metro Station"),
            "bus_stops": sum(1 for p in amenities if p.get("subcategory") in ("Bus Stop", "Bus Terminal")),
            "railway_stations": sum(1 for p in amenities if p.get("subcategory") == "Railway Station"),
            "schools": sum(1 for p in amenities if p.get("subcategory") == "School"),
            "colleges": sum(1 for p in amenities if p.get("subcategory") in ("College", "University")),
            "hospitals": sum(1 for p in amenities if p.get("subcategory") == "Hospital"),
            "clinics": sum(1 for p in amenities if p.get("subcategory") in ("Clinic", "Pharmacy", "Diagnostic Centre")),
            "malls_commercial": sum(1 for p in amenities if p.get("subcategory") == "Mall / Shopping Centre"),
            "supermarkets": sum(1 for p in amenities if p.get("subcategory") in ("Supermarket", "Marketplace")),
            "it_tech_parks": sum(1 for p in amenities if p.get("subcategory") == "IT / Tech Park"),
            "employment_centres": sum(1 for p in amenities if p.get("category") == "Employment"),
            "parks_recreation": sum(1 for p in amenities if p.get("category") == "Recreation"),
            "other_amenities": sum(1 for p in amenities if p.get("category") == "Other Amenities")
        }

        # Nearest facilities identification
        def _get_nearest(filter_fn):
            for a in amenities:
                if filter_fn(a):
                    return {
                        "name": a["name"],
                        "subcategory": a["subcategory"],
                        "distance_km": a["distance_km"],
                        "latitude": a["latitude"],
                        "longitude": a["longitude"]
                    }
            return None

        result["nearest_facilities"] = {
            "nearest_metro": _get_nearest(lambda a: a.get("subcategory") == "Metro Station"),
            "nearest_school": _get_nearest(lambda a: a.get("subcategory") == "School"),
            "nearest_hospital": _get_nearest(lambda a: a.get("subcategory") == "Hospital"),
            "nearest_commercial": _get_nearest(lambda a: a.get("category") == "Commercial"),
            "nearest_it_park": _get_nearest(lambda a: a.get("category") == "Employment"),
            "nearest_bus_stop": _get_nearest(lambda a: a.get("subcategory") in ("Bus Stop", "Bus Terminal"))
        }

        # Recompute nearest micro-market
        nearest_mm, dist_mm = find_nearest_micromarket(new_lat, new_lon)
        result["nearest_micromarket"] = {"name": nearest_mm, "distance_km": dist_mm}

        return result


def get_amenity_service() -> AmenityService:
    return AmenityService.get_instance()
