import json
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
from backend.db.connection import get_db

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "market_demand_model.pkl"
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


def _lookup_micro_market(mm_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up micro-market corridor metrics from verified SQLite database.
    Performs exact match first, then substring match, significant words match,
    and projects table fallback.
    """
    if not mm_name or not mm_name.strip():
        return None

    clean = mm_name.strip()
    with get_db() as db:
        # 1. Exact case-insensitive match
        row = db.query_one("SELECT * FROM micro_markets WHERE LOWER(micromarket_name) = LOWER(?)", (clean,))
        if row:
            return dict(row)

        # 2. Substring match
        row = db.query_one("SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(?)", (f"%{clean}%",))
        if row:
            return dict(row)

        # 3. Individual significant words match (e.g. 'Thanisandra' in 'Thanisandra-Hennur')
        words = [w.strip() for w in clean.replace("-", " ").split() if len(w.strip()) > 3]
        for w in words:
            row = db.query_one("SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(?)", (f"%{w}%",))
            if row:
                return dict(row)

        # 4. Check projects table aggregate if micro_markets row doesn't exist
        proj_row = db.query_one(
            "SELECT micromarket_name, SUM(launched_units) as launched_units, "
            "SUM(absorbed_units) as absorbed_units, SUM(available_units) as available_units, "
            "AVG(percentage_sold) as average_percentage_sold "
            "FROM projects WHERE LOWER(micromarket_name) LIKE LOWER(?) GROUP BY micromarket_name",
            (f"%{clean}%",)
        )
        if proj_row and proj_row["launched_units"]:
            return dict(proj_row)

    return None


def predict_market_absorption(
    micromarket_name: str,
    units: int = 300,
    price_per_sqft: float = 6500.0,
    unsold_inventory_estimate: Optional[float] = None,
    overhang_months_estimate: Optional[float] = None
) -> dict:
    """
    Inference function for Market Demand / Absorption ML Model (RandomForestRegressor).
    Predicts expected absorption rate (%) and absorbed unit volume using real
    micro-market metrics from verified database records.
    """
    model_data = load_model()
    if not model_data:
        return {
            "prediction_type": "absorption",
            "prediction_status": "unavailable",
            "ml_used": False,
            "status": "unavailable",
            "reason": "Market demand model artifact not found at ml/market/market_demand_model.pkl."
        }

    model = model_data["model"]
    scaler = model_data["scaler"]
    feature_cols = model_data["feature_cols"]
    version = model_data.get("model_version", "v1.0.0-rf")

    metadata = {}
    if META_PATH.exists():
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}

    # Handle missing / empty micro-market name
    if not micromarket_name or not str(micromarket_name).strip():
        if unsold_inventory_estimate is None or overhang_months_estimate is None:
            return {
                "prediction_type": "absorption",
                "prediction_status": "unsupported_market",
                "ml_used": False,
                "status": "unavailable",
                "reason": "No micro-market name was provided for database lookup.",
                "missing_features": ["micromarket_name"],
                "fallback": "Bangalore city-wide benchmark median absorption (87.0%) available with 40% confidence discount.",
                "model_name": "Market Demand & Absorption Regressor",
                "model_version": version
            }

    # Query database for real micro-market metrics
    mm_row = _lookup_micro_market(str(micromarket_name).strip()) if micromarket_name else None

    # Determine feature values
    if mm_row is not None:
        launched = mm_row.get("launched_units")
        absorbed = mm_row.get("absorbed_units")
        available = mm_row.get("available_units")

        missing = []
        if launched is None:
            missing.append("launched_units")
        if absorbed is None:
            missing.append("absorbed_units")

        if missing and (unsold_inventory_estimate is None or overhang_months_estimate is None):
            return {
                "prediction_type": "absorption",
                "prediction_status": "missing_features",
                "ml_used": False,
                "status": "unavailable",
                "reason": f"Micro-market '{micromarket_name}' lacks required database features: {', '.join(missing)}.",
                "missing_features": missing,
                "fallback": "Bangalore city-wide benchmark median absorption (87.0%) available with 40% confidence discount.",
                "model_name": "Market Demand & Absorption Regressor",
                "model_version": version
            }

        # Derive model features consistent with training semantics
        unsold_db = float(available if available is not None else (launched - absorbed))
        quarterly_absorption = max(1.0, float(absorbed) / 12.0)
        overhang_db = round((unsold_db / quarterly_absorption) * 3.0, 1)
        total_avail_db = float(launched)

        unsold_val = float(unsold_inventory_estimate) if unsold_inventory_estimate is not None else unsold_db
        overhang_val = float(overhang_months_estimate) if overhang_months_estimate is not None else overhang_db
        total_avail_val = total_avail_db

        matched_market_name = mm_row.get("micromarket_name", micromarket_name)
        db_values = {
            "micromarket_name": matched_market_name,
            "launched_units": launched,
            "absorbed_units": absorbed,
            "available_units": available,
            "average_percentage_sold": mm_row.get("average_percentage_sold")
        }
    else:
        # Micro-market not found in database records
        if unsold_inventory_estimate is not None and overhang_months_estimate is not None:
            unsold_val = float(unsold_inventory_estimate)
            overhang_val = float(overhang_months_estimate)
            total_avail_val = float(units + unsold_val)
            matched_market_name = micromarket_name or "Custom Simulation"
            db_values = None
        else:
            return {
                "prediction_type": "absorption",
                "prediction_status": "unsupported_market",
                "ml_used": False,
                "status": "unavailable",
                "reason": f"Micro-market '{micromarket_name}' was not found in verified database records.",
                "missing_features": ["micro_market_record"],
                "fallback": "Bangalore city-wide benchmark median absorption (87.0%) available with 40% confidence discount.",
                "model_name": "Market Demand & Absorption Regressor",
                "model_version": version
            }

    # Prepare input vector using training feature columns
    input_dict = {
        "unsold_units": unsold_val,
        "overhang_months": overhang_val,
        "total_available": total_avail_val
    }

    input_df = pd.DataFrame([input_dict])[feature_cols]
    input_scaled = scaler.transform(input_df)

    # Pure ML Model Prediction from trained RandomForestRegressor
    raw_prediction_pct = float(model.predict(input_scaled)[0])

    # Transparent post-processing guardrails
    floor_value = 35.0
    ceiling_value = 98.5
    floor_applied = bool(raw_prediction_pct < floor_value)
    ceiling_applied = bool(raw_prediction_pct > ceiling_value)

    predicted_absorption_pct = max(floor_value, min(ceiling_value, round(raw_prediction_pct, 2)))
    predicted_absorbed_units = int(round(units * (predicted_absorption_pct / 100.0)))

    result = {
        "prediction_type": "absorption",
        "prediction_status": "valid",
        "raw_model_prediction_pct": round(raw_prediction_pct, 2),
        "raw_prediction_pct": round(raw_prediction_pct, 2),  # backward compatibility alias
        "predicted_absorption_pct": predicted_absorption_pct,
        "predicted_absorbed_units": predicted_absorbed_units,
        "planned_units": units,
        "unit": "%",
        "model_features": input_dict,
        "post_processing": {
            "floor_applied": floor_applied,
            "floor_value": floor_value,
            "ceiling_applied": ceiling_applied,
            "ceiling_value": ceiling_value
        },
        "model_name": "Market Demand & Absorption Regressor",
        "model_version": version,
        "algorithm": model_data.get("algorithm", "RandomForestRegressor"),
        "evaluation_metrics": metadata.get("evaluation_metrics", {}),
        "ml_used": True,
        "status": "available",
        "method": "Supervised Random Forest Regression trained on historical inventory and absorption data"
    }

    if db_values is not None:
        result["database_values"] = db_values

    return result
