from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.db.connection import get_db

router = APIRouter(
    tags=["City & Micro-Markets"]
)


@router.get("/city/bangalore/profile")
@router.get("/city/bengaluru/profile")
def get_bangalore_profile() -> Dict[str, Any]:
    """
    Returns macro residential market overview for Bengaluru.
    """
    with get_db() as db:
        row = db.query_one("SELECT * FROM cities WHERE city_name = 'Bengaluru'")
    if not row:
        raise HTTPException(status_code=404, detail="Bengaluru profile not found.")
    return dict(row)


@router.get("/city/bangalore/micro-markets")
@router.get("/city/bengaluru/micro-markets")
def get_bangalore_micro_markets() -> List[Dict[str, Any]]:
    """
    Returns all 25 canonical micro-markets in Bengaluru with verified geographic
    coordinates (latitude, longitude) and market indicators for geospatial mapping.
    """
    with get_db() as db:
        rows = db.query(
            """
            SELECT micromarket_id, micromarket_name, zone, latitude, longitude,
                   segment_bias, premium_amenability, launch_activity_signal,
                   absorption_signal, average_price_per_sqft, average_percentage_sold,
                   launched_units, absorbed_units, available_units,
                   key_drivers, notes, source
            FROM micro_markets
            ORDER BY zone, micromarket_name
            """
        )
    return [dict(r) for r in rows]
