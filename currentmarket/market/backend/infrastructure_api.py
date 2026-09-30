from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, HTTPException
from backend.services.amenity_service import get_amenity_service
from backend.services.geospatial_service import resolve_coordinates, is_valid_bengaluru_coordinates

router = APIRouter(
    prefix="/infrastructure",
    tags=["Geospatial & Amenities"]
)


class AmenityQueryRequest(BaseModel):
    latitude: Optional[float] = Field(None, example=12.9255)
    longitude: Optional[float] = Field(None, example=77.5468)
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_km: float = Field(5.0, example=5.0)
    micromarket: Optional[str] = None


@router.get("/amenities")
def get_amenities(
    lat: Optional[float] = Query(None, description="Center latitude"),
    lon: Optional[float] = Query(None, description="Center longitude"),
    latitude: Optional[float] = Query(None, description="Center latitude alias"),
    longitude: Optional[float] = Query(None, description="Center longitude alias"),
    radius_km: float = Query(5.0, description="Search radius in km (default: 5.0)"),
    micromarket: Optional[str] = Query(None, description="Optional micro-market name")
) -> Dict[str, Any]:
    """
    Returns real, verified points of interest within 5 km of coordinates or micro-market
    with Haversine distances across 7 categories: Transport, Education, Healthcare,
    Commercial, Employment, Recreation, Other Amenities.
    """
    try:
        final_lat = lat if lat is not None else latitude
        final_lon = lon if lon is not None else longitude

        if final_lat is not None and final_lon is not None:
            c_lat, c_lon = float(final_lat), float(final_lon)
        elif micromarket:
            c_lat, c_lon = resolve_coordinates(micromarket)
        else:
            c_lat, c_lon = resolve_coordinates("Kanakapura Road")

        amenity_svc = get_amenity_service()
        return amenity_svc.get_amenities_within_radius(
            latitude=c_lat,
            longitude=c_lon,
            radius_km=radius_km
        )
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
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


@router.post("/amenities")
def post_amenities(req: AmenityQueryRequest) -> Dict[str, Any]:
    """
    POST endpoint to retrieve real POIs within 5km from exact coordinates.
    """
    lat = req.latitude if req.latitude is not None else req.lat
    lon = req.longitude if req.longitude is not None else req.lon
    return get_amenities(lat=lat, lon=lon, radius_km=req.radius_km, micromarket=req.micromarket)
