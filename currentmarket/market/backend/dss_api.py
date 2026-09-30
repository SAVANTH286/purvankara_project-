from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.agents.base import ProjectInput
from backend.intelligence.orchestrator import get_orchestrator
from backend.db.connection import get_db

router = APIRouter(
    prefix="/dss",
    tags=["Decision Support System"]
)


@router.post("/evaluate")
def evaluate_project(project: ProjectInput) -> Dict[str, Any]:
    """
    Evaluates a proposed residential project through the 10-Agent Decision Support System.
    Produces an explainable Launch, Hold, or No-launch verdict with evidence coverage and data limitations.
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.evaluate_project(project)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DSS Evaluation Error: {str(e)}")


@router.get("/micromarkets")
def list_micromarkets() -> List[Dict[str, Any]]:
    """
    Returns all 25 canonical Bengaluru micro-markets with verified supply and absorption metrics.
    """
    with get_db() as db:
        rows = db.query(
            """
            SELECT micromarket_id, micromarket_name, zone, segment_bias, premium_amenability,
                   average_price_per_sqft, average_percentage_sold,
                   launched_units, absorbed_units, available_units,
                   launch_activity_signal, absorption_signal, key_drivers, notes, source
            FROM micro_markets
            ORDER BY zone, micromarket_name
            """
        )
    return [dict(r) for r in rows]


@router.get("/city-profile")
def get_city_profile() -> Dict[str, Any]:
    """
    Returns the Bengaluru macro residential market profile from verified consultant research.
    """
    with get_db() as db:
        row = db.query_one("SELECT * FROM cities WHERE city_name = 'Bengaluru'")
    return dict(row) if row else {}


@router.get("/buyer-profiles")
def get_buyer_profiles() -> List[Dict[str, Any]]:
    """
    Returns demographic profile summaries aggregated from real historical project bookings.
    """
    with get_db() as db:
        rows = db.query("SELECT * FROM buyer_profiles ORDER BY id ASC")
    return [dict(r) for r in rows]


@router.get("/projects")
def list_projects(micromarket: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """
    Returns verified competitor and historical projects from database.
    """
    query = "SELECT * FROM projects"
    params = ()
    if micromarket:
        query += " WHERE LOWER(micromarket_name) LIKE LOWER(%s)"
        params = (f"%{micromarket.strip()}%",)
    query += " ORDER BY id ASC"

    with get_db() as db:
        rows = db.query(query, params)
    return [dict(r) for r in rows]
