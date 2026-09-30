from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.engine.scenario_engine import ScenarioRequest, get_scenario_engine

router = APIRouter(
    prefix="/scenario",
    tags=["Scenario Engine"]
)


@router.post("/run")
def run_scenario(req: ScenarioRequest) -> Dict[str, Any]:
    """
    Runs What-If sensitivity analysis (price, unit scale, BHK, delay) through
    Price ML, Market Demand ML, Buyer Fit ML, and Decision Engine.
    Returns baseline vs scenario comparison and quantitative deltas.
    """
    if req.new_price_per_sqft is not None and req.new_price_per_sqft <= 0:
        raise HTTPException(status_code=422, detail="Scenario price per sq.ft must be a positive number greater than 0.")

    if req.new_units is not None and req.new_units <= 0:
        raise HTTPException(status_code=422, detail="Scenario planned units must be a positive integer greater than 0.")

    if req.competitor_launch_month is not None and not (1 <= req.competitor_launch_month <= 12):
        raise HTTPException(status_code=422, detail="competitor_launch_month must be between 1 and 12.")

    if req.intervention_month is not None and not (1 <= req.intervention_month <= 12):
        raise HTTPException(status_code=422, detail="intervention_month must be between 1 and 12.")

    try:
        engine = get_scenario_engine()
        return engine.run_scenario(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario run error: {str(e)}")
