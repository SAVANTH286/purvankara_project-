import json
import pickle
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent
MODEL_V2_1_PATH = MODEL_DIR / "price_model_v2_1.pkl"
META_V2_1_PATH = MODEL_DIR / "model_metadata_v2_1.json"
MODEL_V2_PATH = MODEL_DIR / "price_model_v2.pkl"
META_V2_PATH = MODEL_DIR / "model_metadata_v2.json"
MODEL_V1_PATH = MODEL_DIR / "price_model.pkl"
META_V1_PATH = MODEL_DIR / "model_metadata.json"
COVERAGE_PATH = MODEL_DIR / "market_coverage_registry.json"

_MODEL_V2_1_CACHE = None
_MODEL_V2_CACHE = None
_MODEL_V1_CACHE = None
_COVERAGE_REGISTRY = None


def load_coverage_registry() -> Dict[str, Any]:
    """Loads the empirical 25-corridor coverage registry."""
    global _COVERAGE_REGISTRY
    if _COVERAGE_REGISTRY is None:
        if COVERAGE_PATH.exists():
            try:
                with open(COVERAGE_PATH, "r", encoding="utf-8") as f:
                    _COVERAGE_REGISTRY = json.load(f)
            except Exception:
                _COVERAGE_REGISTRY = {}
        else:
            _COVERAGE_REGISTRY = {}
    return _COVERAGE_REGISTRY


def load_model(version: Optional[str] = None):
    """
    Loads Price ML model artifact.
    Defaults to v2 (Regularized Ridge on 53 verified project observations) if available.
    Supports v2.1 if requested via version='v2.1'.
    Falls back to v1.1.0-gbr if v2 is not present or if explicitly requested.
    """
    global _MODEL_V2_1_CACHE, _MODEL_V2_CACHE, _MODEL_V1_CACHE

    req_v2_1 = version and ("v2.1" in str(version).lower() or "v2_1" in str(version).lower())
    req_v1 = version and "v1" in str(version).lower()

    if req_v2_1 and MODEL_V2_1_PATH.exists():
        if _MODEL_V2_1_CACHE is None:
            with open(MODEL_V2_1_PATH, "rb") as f:
                _MODEL_V2_1_CACHE = pickle.load(f)
        return _MODEL_V2_1_CACHE

    if not req_v1 and MODEL_V2_PATH.exists():
        if _MODEL_V2_CACHE is None:
            with open(MODEL_V2_PATH, "rb") as f:
                _MODEL_V2_CACHE = pickle.load(f)
        return _MODEL_V2_CACHE

    if MODEL_V1_PATH.exists():
        if _MODEL_V1_CACHE is None:
            with open(MODEL_V1_PATH, "rb") as f:
                _MODEL_V1_CACHE = pickle.load(f)
        return _MODEL_V1_CACHE

    return None


def resolve_canonical_micro_market(mm_name: str, registry: Dict[str, Any]) -> Optional[str]:
    """
    Resolves raw or colloquial corridor names to one of the 25 canonical micro-markets.
    Returns None if the market is invalid, unknown, or outside Bengaluru.
    """
    clean = str(mm_name or "").strip().lower()
    if not clean:
        return None

    # 1. Exact match against registry keys
    for mm in registry:
        if clean == mm.lower():
            return mm

    # 2. Token-boundary alias resolution
    alias_map = {
        "bagaluru": "Bagalur",
        "bagalur": "Bagalur",
        "kanakapura": "Kanakapura Road",
        "devanahalli": "Devanahalli-Airport Road",
        "outer ring road": "ORR Marathahalli-Sarjapur-HSR",
        "marathahalli": "ORR Marathahalli-Sarjapur-HSR",
        "panathur": "ORR Marathahalli-Sarjapur-HSR",
        "hsr": "ORR Marathahalli-Sarjapur-HSR",
        "orr": "ORR Marathahalli-Sarjapur-HSR",
        "sarjapur": "Sarjapur Road",
        "hennur": "Thanisandra-Hennur",
        "thanisandra": "Thanisandra-Hennur",
        "budigere": "Old Madras Road-Budigere Cross",
        "omr": "Old Madras Road-Budigere Cross",
        "old madras road": "Old Madras Road-Budigere Cross",
        "lavelle": "CBD Lavelle-MG-Richmond",
        "mg road": "CBD Lavelle-MG-Richmond",
        "cbd": "CBD Lavelle-MG-Richmond",
        "yelahanka": "Jakkur-Yelahanka",
        "jakkur": "Jakkur-Yelahanka",
        "hebbal": "Hebbal-Bellary Road",
        "bellary road": "Hebbal-Bellary Road",
        "kengeri": "Mysore Road-Uttarahalli-Magadi Road",
        "mysore road": "Mysore Road-Uttarahalli-Magadi Road",
        "electronic city": "Electronic City",
        "koramangala": "Koramangala",
        "indiranagar": "Indiranagar-Richmond Town-Vasanth Nagar",
        "richmond town": "Indiranagar-Richmond Town-Vasanth Nagar",
        "vasanth nagar": "Indiranagar-Richmond Town-Vasanth Nagar",
        "hosur road": "Hosur Road-Begur",
        "begur": "Hosur Road-Begur",
        "bommanahalli": "Hosur Road-Begur",
        "attibele": "Attibele-Chandapur",
        "chandapur": "Attibele-Chandapur",
        "chandapura": "Attibele-Chandapur",
        "btm": "BTM Layout",
        "bannerghatta": "Bannerghatta Road",
        "jp nagar": "JP Nagar-Jayanagar-Banashankari",
        "jayanagar": "JP Nagar-Jayanagar-Banashankari",
        "banashankari": "JP Nagar-Jayanagar-Banashankari",
        "malleshwaram": "Malleshwaram-Rajajinagar-Yeshwanthpur",
        "rajajinagar": "Malleshwaram-Rajajinagar-Yeshwanthpur",
        "yeshwanthpur": "Malleshwaram-Rajajinagar-Yeshwanthpur",
        "frazer town": "Off-Central Frazer-Benson-Richards-Dollars Colony",
        "dollars colony": "Off-Central Frazer-Benson-Richards-Dollars Colony",
        "old airport road": "Old Airport Road-Marathahalli-KR Puram",
        "kr puram": "Old Airport Road-Marathahalli-KR Puram",
        "tumkur road": "Tumkur Road-Vijayanagar",
        "vijayanagar": "Tumkur Road-Vijayanagar",
        "hoskote": "Hoskote"
    }

    for alias, canon in alias_map.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", clean):
            return canon

    # 3. Substring match only for distinct terms >= 5 chars
    if len(clean) >= 5:
        for mm in registry:
            if clean in mm.lower():
                return mm

    return None


def predict_price_per_sqft(
    micromarket_name: str,
    property_segment: str = "Mid",
    property_type: str = "Residential",
    bhk_str: str = "3BHK",
    units: int = 300,
    model_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Coverage-aware inference function for Puravankara Price Intelligence.
    Returns predicted new launch price per sq.ft along with empirical evidence,
    data provenance, and explicit coverage tier (OBSERVED, LIMITED, CONFIGURATION_BASELINE, UNSUPPORTED).
    """
    registry = load_coverage_registry()
    model_data = load_model(version=model_version)

    if not model_data:
        return {
            "prediction": None,
            "predicted_price_per_sqft": None,
            "raw_prediction": None,
            "prediction_type": "price_per_sqft",
            "unit": "INR / sq.ft",
            "ml_used": False,
            "coverage_status": "UNSUPPORTED",
            "confidence_status": "UNSUPPORTED",
            "coverage_reason": "Price prediction model artifact not found.",
            "warning": "Model artifact unavailable. Ingest verified data and run training.",
            "coverage_warning": "Model artifact unavailable.",
            "training_observation_count": 0,
            "training_market_count": 0,
            "market_observation_count": 0,
            "market_development_count": 0,
            "market_developer_count": 0,
            "latest_verified_launch_date": None,
            "comparable_projects": [],
            "model_name": "Price Intelligence Regressor",
            "model_version": "unavailable",
            "status": "unavailable"
        }

    # 1. Resolve canonical micro-market
    canon_mm = resolve_canonical_micro_market(micromarket_name, registry)
    if not canon_mm:
        raw_name = str(micromarket_name or "").strip()
        reason = (
            f"Micro-market '{raw_name}' is not recognized as one of the 25 canonical Bengaluru corridors."
            if raw_name else "Micro-market name was not provided."
        )
        return {
            "prediction": None,
            "predicted_price_per_sqft": None,
            "raw_prediction": None,
            "prediction_type": "price_per_sqft",
            "unit": "INR / sq.ft",
            "ml_used": False,
            "coverage_status": "UNSUPPORTED",
            "confidence_status": "UNSUPPORTED",
            "coverage_reason": reason,
            "warning": f"Unsupported corridor: {reason} No responsible ML estimate can be generated.",
            "coverage_warning": f"Unsupported corridor: {reason}",
            "training_observation_count": model_data.get("training_rows", 53),
            "training_market_count": model_data.get("training_micro_markets", 15),
            "market_observation_count": 0,
            "market_development_count": 0,
            "market_developer_count": 0,
            "latest_verified_launch_date": None,
            "comparable_projects": [],
            "model_name": "Price Intelligence Regressor",
            "model_version": model_data.get("model_version", "v2.0.0-ridge"),
            "status": "unsupported"
        }

    # 2. Extract market empirical evidence from registry
    m_info = registry.get(canon_mm, {})
    m_obs = m_info.get("observation_count", 0)
    m_devs = m_info.get("development_count", 0)
    m_builders = m_info.get("developer_count", 0)
    m_latest = m_info.get("latest_launch_date")
    m_comps = m_info.get("comparable_projects", [])
    coverage_tier = m_info.get("coverage_tier", "CONFIGURATION_BASELINE")
    confidence_status = m_info.get("confidence_status", "LOW")
    coverage_reason = m_info.get("coverage_reason", "")
    coverage_warning = m_info.get("warning")

    # 3. Robust input normalization
    warnings_list = []
    if coverage_warning:
        warnings_list.append(coverage_warning)

    # BHK normalization
    bhk = 3.0
    bhk_s = str(bhk_str or "").upper().strip()
    if "1" in bhk_s:
        bhk = 1.0
    elif "2" in bhk_s:
        bhk = 2.0
    elif "4" in bhk_s:
        bhk = 4.0
    elif "5" in bhk_s:
        bhk = 5.0
    elif "3" in bhk_s:
        bhk = 3.0
    else:
        warnings_list.append(f"Unspecified BHK configuration '{bhk_str}'; defaulted to 3.0 BHK standard benchmark.")
        bhk = 3.0

    # Units normalization
    try:
        units_val = int(units) if units is not None else 300
        if units_val <= 0:
            units_val = 300
            warnings_list.append("Proposed unit count <= 0; defaulted to 300 units.")
    except Exception:
        units_val = 300
        warnings_list.append(f"Invalid units value '{units}'; defaulted to 300 units.")

    # Unit size estimation based on BHK
    unit_size_map = {1.0: 650.0, 2.0: 1050.0, 3.0: 1550.0, 4.0: 2400.0, 5.0: 3400.0}
    unit_size = unit_size_map.get(bhk, 1550.0)

    # Segment one-hots
    seg_lower = str(property_segment or "Mid").lower()
    is_luxury = 1 if ("lux" in seg_lower or "ultra" in seg_lower) else 0
    is_premium = 1 if ("prem" in seg_lower and not is_luxury) else 0
    is_mid = 1 if (not is_luxury and not is_premium) else 0

    # 4. Feature vector construction
    active_version = model_data.get("model_version", "v2.0.0-ridge")
    model = model_data["model"]
    scaler = model_data["scaler"]
    feature_cols = model_data["feature_cols"]

    if "average_unit_size_sqft" in feature_cols:
        # v2.1.0-ridge model with harmonized average_unit_size_sqft
        zone_map = model_data.get("zone_map", {})
        corridor_zone = zone_map.get(canon_mm, m_info.get("zone", "North"))
        input_dict = {
            "units": float(units_val),
            "bhk": float(bhk),
            "average_unit_size_sqft": float(unit_size),
            "is_luxury": is_luxury,
            "is_premium": is_premium,
            "is_mid": is_mid,
            "zone_north": 1 if corridor_zone == "North" else 0,
            "zone_east": 1 if corridor_zone == "East" else 0,
            "zone_south": 1 if corridor_zone == "South" else 0,
            "zone_central": 1 if corridor_zone == "Central" else 0
        }
    elif "zone_north" in feature_cols:
        # v2.0.0-ridge model with macro zones
        zone_map = model_data.get("zone_map", {})
        corridor_zone = zone_map.get(canon_mm, m_info.get("zone", "North"))
        input_dict = {
            "units": float(units_val),
            "bhk": float(bhk),
            "unit_size": float(unit_size),
            "is_luxury": is_luxury,
            "is_premium": is_premium,
            "is_mid": is_mid,
            "zone_north": 1 if corridor_zone == "North" else 0,
            "zone_east": 1 if corridor_zone == "East" else 0,
            "zone_south": 1 if corridor_zone == "South" else 0,
            "zone_central": 1 if corridor_zone == "Central" else 0
        }
    else:
        # v1.1.0-gbr legacy fallback
        input_dict = {
            "units": float(units_val),
            "bhk": float(bhk),
            "is_luxury": is_luxury,
            "is_premium": is_premium,
            "is_mid": is_mid
        }

    input_df = pd.DataFrame([input_dict])[feature_cols]
    input_scaled = scaler.transform(input_df)

    raw_prediction = float(model.predict(input_scaled)[0])
    # Realistic bounding (minimum ₹3,500/sqft, maximum ₹35,000/sqft)
    bounded_prediction = max(3500.0, min(35000.0, raw_prediction))
    predicted_price = round(bounded_prediction, -1)  # rounded to nearest 10 INR

    # Consolidated human-readable warning
    combined_warning = " | ".join(warnings_list) if warnings_list else None

    # Structural evidence summary
    evidence_payload = {
        "verified_observations": m_obs,
        "verified_developments": m_devs,
        "verified_developers": m_builders,
        "latest_verified_launch_date": m_latest,
        "comparable_projects": m_comps,
        "corridor_price_range": {
            "min": m_info.get("price_min"),
            "max": m_info.get("price_max"),
            "median": m_info.get("price_median"),
            "mean": m_info.get("price_mean")
        } if m_obs > 0 else None
    }

    return {
        "prediction": int(predicted_price),
        "predicted_price_per_sqft": int(predicted_price),
        "raw_prediction": round(raw_prediction, 1),
        "prediction_type": "price_per_sqft",
        "unit": "INR / sq.ft",
        "ml_used": True,
        "coverage_status": coverage_tier,
        "coverage_reason": coverage_reason,
        "confidence_status": confidence_status,
        "warning": combined_warning,
        "coverage_warning": combined_warning,
        "training_observation_count": model_data.get("training_rows", 53),
        "training_market_count": model_data.get("training_micro_markets", 15),
        "market_observation_count": m_obs,
        "market_development_count": m_devs,
        "market_developer_count": m_builders,
        "latest_verified_launch_date": m_latest,
        "comparable_projects": m_comps,
        "model_name": model_data.get("model_name", "Price Intelligence Regressor"),
        "model_version": active_version,
        "algorithm": model_data.get("algorithm", "Regularized Ridge Regression"),
        "evidence": evidence_payload,
        "feature_coverage": {
            "canonical_micro_market": canon_mm,
            "raw_location_input": micromarket_name,
            "property_segment": property_segment,
            "bhk": bhk_str,
            "bhk_numeric": bhk,
            "units": units_val,
            "estimated_unit_size_sqft": unit_size
        },
        "status": "available",
        "method": f"Supervised {model_data.get('algorithm', 'Regression')} trained on verified project launch records",
        "limitations": [
            "Model is trained exclusively on dual-verified statutory filings and RERA gazettes.",
            "Predictions in LIMITED_MARKET corridors are anchored on zonal trendlines and segment scaling.",
            "Predictions in CONFIGURATION_BASELINE corridors reflect citywide cross-market configuration baselines, not local cleared transaction rates."
        ]
    }
