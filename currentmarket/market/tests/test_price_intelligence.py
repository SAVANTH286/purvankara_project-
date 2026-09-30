import json
import pytest
import pandas as pd
from pathlib import Path
from ml.price.infer import predict_price_per_sqft
from backend.intelligence.tool_registry import execute_tool
from backend.agents.base import ProjectInput
from backend.intelligence.orchestrator import get_orchestrator

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAIN_CSV = REPO_ROOT / "ml" / "price" / "verified_price_training_dataset.csv"
CAND_CSV = REPO_ROOT / "price_ml_phase3c_candidates.csv"


# 1. Known supported market
def test_known_supported_market():
    res = predict_price_per_sqft("Bagalur", "Mid", "Residential", "3BHK", 300)
    assert res["coverage_status"] == "OBSERVED_MARKET"
    assert res["confidence_status"] == "HIGH"
    assert res["market_observation_count"] == 18
    assert res["market_development_count"] == 9
    assert res["prediction"] is not None
    assert res["prediction"] > 5000 and res["prediction"] < 15000
    assert res["ml_used"] is True


# 2. Limited market
def test_limited_market():
    # Whitefield (6 obs)
    res_wf = predict_price_per_sqft("Whitefield", "Premium", "Residential", "3BHK", 400)
    assert res_wf["coverage_status"] == "LIMITED_MARKET"
    assert res_wf["confidence_status"] == "MEDIUM"
    assert res_wf["market_observation_count"] == 6
    assert res_wf["warning"] is not None
    assert "Moderate market evidence" in res_wf["warning"]

    # Devanahalli (3 obs)
    res_dev = predict_price_per_sqft("Devanahalli", "Mid", "Residential", "3BHK", 300)
    assert res_dev["coverage_status"] == "LIMITED_MARKET"
    assert res_dev["confidence_status"] == "LOW"
    assert res_dev["market_observation_count"] == 3
    assert "Limited market evidence" in res_dev["warning"]


# 3. Unsupported market
def test_unsupported_market():
    res = predict_price_per_sqft("Mumbai Metro Corridor", "Mid", "Residential", "3BHK", 300)
    assert res["coverage_status"] == "UNSUPPORTED"
    assert res["confidence_status"] == "UNSUPPORTED"
    assert res["prediction"] is None
    assert res["ml_used"] is False
    assert "not recognized" in res["warning"]


# 4. Missing BHK configuration
def test_missing_bhk_graceful_fallback():
    res = predict_price_per_sqft("Whitefield", "Mid", "Residential", None, 300)
    assert res["prediction"] is not None
    assert res["coverage_status"] == "LIMITED_MARKET"
    assert "Unspecified BHK" in res["warning"]
    assert res["feature_coverage"]["bhk_numeric"] == 3.0


# 5. Missing / invalid units
def test_missing_units_graceful_fallback():
    res = predict_price_per_sqft("Whitefield", "Mid", "Residential", "2BHK", -50)
    assert res["prediction"] is not None
    assert "defaulted to 300" in res["warning"]
    assert res["feature_coverage"]["units"] == 300


# 6. Invalid micro-market (empty / none)
def test_invalid_micro_market():
    res_none = predict_price_per_sqft(None)
    assert res_none["coverage_status"] == "UNSUPPORTED"
    assert res_none["prediction"] is None
    assert res_none["ml_used"] is False

    res_empty = predict_price_per_sqft("   ")
    assert res_empty["coverage_status"] == "UNSUPPORTED"
    assert res_empty["prediction"] is None


# 7. New proposed project inference (leakage-free)
def test_new_proposed_project_leakage_free():
    res = predict_price_per_sqft("Kanakapura Road", "Mid", "Residential", "3BHK", 350)
    assert res["prediction"] is not None
    assert res["coverage_status"] == "LIMITED_MARKET"
    # Ensure no target or post-launch leakage in feature vector
    fc = res["feature_coverage"]
    assert "sold_pct" not in fc
    assert "absorbed_units" not in fc
    assert "current_inventory" not in fc


# 8. Duplicate project exclusion
def test_duplicate_project_exclusion():
    cand_df = pd.read_csv(CAND_CSV)
    dups = cand_df[cand_df["data_quality_status"] == "DUPLICATE"]
    dup_names = set(dups["project_name"].str.strip())
    assert len(dup_names) >= 4

    train_df = pd.read_csv(TRAIN_CSV)
    # The duplicate records from Phase 3C must NOT be present as duplicate entries
    # E.g. Godrej Ananda Phase 3 was quarantined as DUPLICATE
    assert "Godrej Ananda Phase 3" not in set(train_df["project_name"].str.strip())


# 9. Historical / quarantined record exclusion
def test_historical_quarantined_record_exclusion():
    cand_df = pd.read_csv(CAND_CSV)
    quar = cand_df[cand_df["data_quality_status"] == "QUARANTINED_HISTORICAL"]
    quar_names = set(quar["project_name"].str.strip())

    train_df = pd.read_csv(TRAIN_CSV)
    train_names = set(train_df["project_name"].str.strip())

    # None of the quarantined historical project observations may enter the training dataset
    overlap = quar_names.intersection(train_names)
    assert len(overlap) == 0, f"Quarantined records found in training data: {overlap}"


# 10. Synthetic fixture exclusion
def test_synthetic_fixture_exclusion():
    train_df = pd.read_csv(TRAIN_CSV)
    # Zero synthetic sources
    assert all(train_df["source_quality"] == "ACCEPTED")
    assert not any("synthetic" in str(s).lower() for s in train_df["source"])
    assert not any("consultant benchmark" in str(s).lower() for s in train_df["source"])


# 11. Price semantics (Target variable consistency)
def test_price_semantics_target_consistency():
    train_df = pd.read_csv(TRAIN_CSV)
    assert all(train_df["price_type"] == "new_launch")
    # All prices must be within realistic new launch realization bounds
    assert train_df["price_per_sqft"].min() >= 3500.0
    assert train_df["price_per_sqft"].max() <= 35000.0


# 12. DSS Integration
def test_dss_orchestrator_price_integration():
    orch = get_orchestrator()
    proj = ProjectInput(
        project_name="Purva Whitefield Grand",
        developer="Puravankara",
        location="Whitefield",
        micro_market="Whitefield",
        property_segment="Premium",
        property_type="Residential",
        bhk="3BHK",
        units=300,
        price_per_sqft=10500.0
    )
    eval_res = orch.evaluate_project(proj)
    assert "price_evidence" in eval_res
    pe = eval_res["price_evidence"]
    assert pe["prediction"] is not None
    assert pe["coverage_status"] == "LIMITED_MARKET"
    assert pe["observations"] == 6
    assert pe["model_version"] == "v2.0.0-ridge"
    assert any("Price Intelligence" in obs for obs in eval_res["observations"])


# 13. Copilot tool integration
def test_copilot_tool_integration():
    tool_res = execute_tool("predict_price", {
        "micromarket_name": "Whitefield",
        "property_segment": "Premium",
        "bhk_str": "3BHK",
        "units": 400
    })
    assert tool_res["status"] == "success"
    data = tool_res["data"]
    assert data["predicted_price_per_sqft"] is not None
    assert data["coverage_status"] == "LIMITED_MARKET"
    assert len(data["comparable_projects"]) > 0
    assert "source" in tool_res
    assert "v2.0.0-ridge" in tool_res["source"]
