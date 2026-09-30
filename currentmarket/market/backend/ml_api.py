from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from ml.buyer.infer import evaluate_buyer_fit
from backend.db.connection import get_db

router = APIRouter(
    prefix="/ml",
    tags=["ML Predictions"]
)


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


@router.post("/market/predict")
def predict_market(req: MarketPredictRequest) -> Dict[str, Any]:
    """
    Predicts expected residential absorption % and volume using the real
    Random Forest Regressor trained on historical inventory and launch trends.
    """
    try:
        return predict_market_absorption(
            micromarket_name=req.micromarket_name,
            units=req.units,
            price_per_sqft=req.price_per_sqft,
            unsold_inventory_estimate=req.unsold_inventory_estimate,
            overhang_months_estimate=req.overhang_months_estimate
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market ML error: {str(e)}")


@router.post("/price/predict")
def predict_price(req: PricePredictRequest) -> Dict[str, Any]:
    """
    Predicts market-clearing realization (INR/sq.ft) using the real
    Gradient Boosting Regressor trained on project pricing datasets.
    """
    try:
        return predict_price_per_sqft(
            micromarket_name=req.micromarket_name,
            property_segment=req.property_segment,
            property_type=req.property_type or "Residential",
            bhk_str=req.bhk or "3BHK",
            units=req.units or 300
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price ML error: {str(e)}")


@router.post("/buyer/predict")
def predict_buyer(req: BuyerPredictRequest) -> Dict[str, Any]:
    """
    Evaluates buyer demographic cluster compatibility and fit score using
    the real KMeans model trained on 2,583 buyer records.
    """
    try:
        return evaluate_buyer_fit(
            bhk_str=req.bhk,
            property_segment=req.property_segment,
            price_per_sqft=req.price_per_sqft,
            units=req.units
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Buyer ML error: {str(e)}")


@router.get("/models")
def list_registered_models() -> List[Dict[str, Any]]:
    """
    Returns the Model Registry catalog from database table `model_versions`.
    """
    with get_db() as db:
        rows = db.query(
            """
            SELECT id, model_name, version, algorithm, training_date,
                   dataset_size, features, evaluation_metric, evaluation_value,
                   artifact_path, status
            FROM model_versions
            ORDER BY id ASC
            """
        )
    return [dict(r) for r in rows]
