"""
backend/external_router.py
--------------------------
Protected external API router for the Puravankara AI DSS.

All endpoints in this router require the X-API-Key header to be present
and valid (matched against PURVANKARA_API_KEY in .env).

Base path: /external/v1/

This router is ONLY for authorized external projects integrating with the
Puravankara AI Decision Support System. The existing dashboard routes at
/api/... and bare /... are completely separate and unchanged.

Endpoint mapping:
    POST /external/v1/dss/evaluate       → DSS 10-agent evaluation
    POST /external/v1/copilot/chat       → AI Copilot (LLM orchestrated)
    POST /external/v1/ml/market/predict  → Market absorption ML
    POST /external/v1/ml/price/predict   → Price per sqft ML
    POST /external/v1/ml/buyer/predict   → Buyer fit ML
    POST /external/v1/scenario/run       → What-If Scenario Engine
    GET  /external/v1/health             → Auth-confirmed health check
"""

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.auth import require_api_key

# Import the same service functions used by the existing internal routes
from backend.agents.base import ProjectInput
from backend.intelligence.orchestrator import get_orchestrator
from backend.copilot.copilot_service import get_copilot_service
from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from ml.buyer.infer import evaluate_buyer_fit
from backend.engine.scenario_engine import ScenarioRequest, get_scenario_engine


# ---------------------------------------------------------------------------
# Router — all routes require API key authentication at the router level
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/external/v1",
    tags=["External Integration API (Authenticated)"],
    dependencies=[Depends(require_api_key)],
)


# ---------------------------------------------------------------------------
# Health check — confirms authentication works
# ---------------------------------------------------------------------------

@router.get("/health")
def external_health_check() -> Dict[str, Any]:
    """
    Authenticated liveness check for external integrations.
    A successful response (200) confirms the API key is valid.
    """
    return {
        "status": "authenticated",
        "service": "PURAVANKARA AI — External Integration API",
        "version": "1.0.0",
        "endpoints": [
            "POST /external/v1/dss/evaluate",
            "POST /external/v1/copilot/chat",
            "POST /external/v1/ml/market/predict",
            "POST /external/v1/ml/price/predict",
            "POST /external/v1/ml/buyer/predict",
            "POST /external/v1/scenario/run",
        ],
    }


# ---------------------------------------------------------------------------
# DSS — 10-Agent Decision Support System
# ---------------------------------------------------------------------------

@router.post("/dss/evaluate")
def external_evaluate_project(project: ProjectInput) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Evaluates a proposed residential project through the
    10-Agent Decision Support System. Returns a Launch, Hold, or No-launch
    verdict with evidence coverage and explainability data.

    Requires X-API-Key header.
    """
    try:
        orchestrator = get_orchestrator()
        return orchestrator.evaluate_project(project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DSS Evaluation Error: {str(e)}")


# ---------------------------------------------------------------------------
# AI Copilot — LLM Orchestrated Chat
# ---------------------------------------------------------------------------

class ExternalChatMessage(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="What is the absorption rate in Kanakapura Road?")


class ExternalChatRequest(BaseModel):
    message: str = Field(..., example="What is the absorption rate in Kanakapura Road?")
    history: Optional[List[ExternalChatMessage]] = Field(default_factory=list)


@router.post("/copilot/chat")
def external_copilot_chat(req: ExternalChatRequest) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Interacts with the Puravankara AI Copilot.
    Two-stage LLM orchestration: routes to specialist agents then synthesizes
    grounded responses from real database and ML evidence.

    Requires X-API-Key header.
    """
    try:
        service = get_copilot_service()
        history_dicts = [{"role": m.role, "content": m.content} for m in (req.history or [])]
        return service.chat(req.message, history_dicts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot Error: {str(e)}")


# ---------------------------------------------------------------------------
# ML Predictions
# ---------------------------------------------------------------------------

class MarketPredictRequest(BaseModel):
    micromarket_name: str = Field(..., example="Kanakapura Road")
    units: int = Field(300, example=300)
    price_per_sqft: float = Field(6500.0, example=6500.0)
    unsold_inventory_estimate: Optional[float] = None
    overhang_months_estimate: Optional[float] = None


class PricePredictRequest(BaseModel):
    micromarket_name: str = Field(..., example="Kanakapura Road")
    property_segment: str = Field("Mid", example="Mid")
    property_type: Optional[str] = "Residential"
    bhk: Optional[str] = "3BHK"
    units: Optional[int] = 300


class BuyerPredictRequest(BaseModel):
    bhk: str = Field("3BHK", example="3BHK")
    property_segment: str = Field("Mid", example="Mid")
    price_per_sqft: float = Field(6500.0, example=6500.0)
    units: Optional[int] = Field(300, example=300)


@router.post("/ml/market/predict")
def external_predict_market(req: MarketPredictRequest) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Predicts expected residential absorption % and volume
    using the Random Forest Regressor trained on historical inventory data.

    Requires X-API-Key header.
    """
    try:
        return predict_market_absorption(
            micromarket_name=req.micromarket_name,
            units=req.units,
            price_per_sqft=req.price_per_sqft,
            unsold_inventory_estimate=req.unsold_inventory_estimate,
            overhang_months_estimate=req.overhang_months_estimate,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market ML error: {str(e)}")


@router.post("/ml/price/predict")
def external_predict_price(req: PricePredictRequest) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Predicts market-clearing realization (INR/sq.ft) using
    the Gradient Boosting Regressor trained on project pricing datasets.

    Requires X-API-Key header.
    """
    try:
        return predict_price_per_sqft(
            micromarket_name=req.micromarket_name,
            property_segment=req.property_segment,
            property_type=req.property_type or "Residential",
            bhk_str=req.bhk or "3BHK",
            units=req.units or 300,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price ML error: {str(e)}")


@router.post("/ml/buyer/predict")
def external_predict_buyer(req: BuyerPredictRequest) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Evaluates buyer demographic cluster compatibility and fit
    score using the KMeans model trained on 2,583 buyer records.

    Requires X-API-Key header.
    """
    try:
        return evaluate_buyer_fit(
            bhk_str=req.bhk,
            property_segment=req.property_segment,
            price_per_sqft=req.price_per_sqft,
            units=req.units,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Buyer ML error: {str(e)}")


# ---------------------------------------------------------------------------
# Scenario Engine — What-If Analysis
# ---------------------------------------------------------------------------

@router.post("/scenario/run")
def external_run_scenario(req: ScenarioRequest) -> Dict[str, Any]:
    """
    [AUTHENTICATED] Runs What-If sensitivity analysis (price, unit scale,
    BHK mix, launch delay, competitor timing) through the full engine stack:
    Price ML → Market Demand ML → Buyer Fit ML → Decision Engine.

    Returns baseline vs scenario comparison with quantitative deltas.

    Requires X-API-Key header.
    """
    if req.new_price_per_sqft is not None and req.new_price_per_sqft <= 0:
        raise HTTPException(
            status_code=422,
            detail="Scenario price per sq.ft must be a positive number greater than 0.",
        )
    if req.new_units is not None and req.new_units <= 0:
        raise HTTPException(
            status_code=422,
            detail="Scenario planned units must be a positive integer greater than 0.",
        )
    if req.competitor_launch_month is not None and not (1 <= req.competitor_launch_month <= 12):
        raise HTTPException(
            status_code=422,
            detail="competitor_launch_month must be between 1 and 12.",
        )
    if req.intervention_month is not None and not (1 <= req.intervention_month <= 12):
        raise HTTPException(
            status_code=422,
            detail="intervention_month must be between 1 and 12.",
        )
    try:
        engine = get_scenario_engine()
        return engine.run_scenario(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario run error: {str(e)}")
