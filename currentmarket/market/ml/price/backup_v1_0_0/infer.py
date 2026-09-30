import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "price_model.pkl"
META_PATH = MODEL_DIR / "model_metadata.json"

_MODEL_CACHE = None


def load_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        if not MODEL_PATH.exists():
            return None
        with open(MODEL_PATH, "rb") as f:
            _MODEL_CACHE = pickle.load(f)
    return _MODEL_CACHE


def predict_price_per_sqft(
    micromarket_name: str,
    property_segment: str,
    property_type: str = "Residential",
    bhk_str: str = "3BHK",
    units: int = 300
) -> dict:
    """
    Inference function for Project Price Prediction ML Model.
    Predicts optimal price per sq.ft based on location, segment, unit scale, and configuration.
    """
    model_data = load_model()
    if not model_data:
        return {
            "prediction_type": "price_per_sqft",
            "ml_used": False,
            "status": "unavailable",
            "reason": "Price prediction model artifact not found."
        }

    model = model_data["model"]
    scaler = model_data["scaler"]
    feature_cols = model_data["feature_cols"]
    version = model_data["model_version"]

    metadata = {}
    if META_PATH.exists():
        with open(META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    # Parse BHK number
    bhk_s = str(bhk_str or "3BHK")
    bhk = 3.0
    if "1" in bhk_s:
        bhk = 1.0
    elif "2" in bhk_s:
        bhk = 2.0
    elif "4" in bhk_s:
        bhk = 4.0

    seg_lower = str(property_segment or "Mid").lower()
    is_luxury = 1 if "lux" in seg_lower else 0
    is_premium = 1 if "prem" in seg_lower or "high" in seg_lower else 0
    is_mid = 1 if (not is_luxury and not is_premium) else 0

    # Zone mapping
    mm_lower = micromarket_name.lower()
    if any(k in mm_lower for k in ["cbd", "indiranagar", "vasanth", "lavelle"]):
        zone_code = 4  # Central
    elif any(k in mm_lower for k in ["whitefield", "airport road", "marathahalli", "budigere", "hoskote", "sarjapur", "orr"]):
        zone_code = 3  # East / South-East
    elif any(k in mm_lower for k in ["kanakapura", "jp nagar", "bannerghatta", "btm", "electronic", "begur", "koramangala"]):
        zone_code = 2  # South
    elif any(k in mm_lower for k in ["mysore", "tumkur", "vijayanagar", "magadi"]):
        zone_code = 5  # West
    else:
        zone_code = 1  # North (Hebbal, Bagalur, Thanisandra, Yelahanka, Devanahalli)

    input_dict = {
        "units": float(units),
        "bhk": float(bhk),
        "sold_pct": 88.0,
        "is_luxury": is_luxury,
        "is_premium": is_premium,
        "is_mid": is_mid,
        "zone_code": float(zone_code)
    }

    input_df = pd.DataFrame([input_dict])[feature_cols]
    input_scaled = scaler.transform(input_df)

    predicted_price = float(model.predict(input_scaled)[0])
    predicted_price = max(4500.0, min(35000.0, round(predicted_price, 0)))

    return {
        "prediction_type": "price_per_sqft",
        "predicted_price_per_sqft": predicted_price,
        "unit": "INR / sq.ft",
        "model_name": "Project Price Prediction Regressor",
        "model_version": version,
        "algorithm": model_data.get("algorithm", "GradientBoostingRegressor"),
        "evaluation_metrics": metadata.get("evaluation_metrics", {}),
        "feature_coverage": {
            "micro_market": micromarket_name,
            "property_segment": property_segment,
            "bhk": bhk_str,
            "units": units
        },
        "ml_used": True,
        "status": "available",
        "method": "Supervised Gradient Boosting Regression trained on verified project transaction prices",
        "limitations": [
            "Prediction models market-clearing realization based on product segment, unit scale, and micro-market zone.",
            "Site-specific premiums (lake facing, corner plot) require architectural adjustment."
        ]
    }
