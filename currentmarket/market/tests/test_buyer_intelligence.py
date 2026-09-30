"""
tests/test_buyer_intelligence.py

Comprehensive test suite verifying Buyer Intelligence V2:
- Empirical demographic distributions from 2,583 customer bookings (Atmosphere, Blubelle, Ecopolitan).
- K-Means clustering preservation (k=5, Silhouette 0.7209).
- Categorical alignment rating tiers (Strong, Moderate, Limited, Insufficient).
- Location-agnostic governance notices and income reporting disclosures.
- BuyerAgent evidence generation and tool registry execution.
- ML API /ml/buyer/predict endpoint schema and backward compatibility.
"""

import pytest
from fastapi.testclient import TestClient

from ml.buyer.buyer_profiles_catalog import (
    BUYER_MODEL_METADATA,
    OVERALL_BUYER_COHORT,
    CLUSTER_PROFILES,
    get_canonical_bhk,
    evaluate_categorical_alignment,
    get_all_segment_alignments
)
from ml.buyer.infer import evaluate_buyer_fit
from backend.agents.buyer_agent import BuyerAgent
from backend.agents.base import ProjectInput
from backend.intelligence.tool_registry import execute_tool, TOOL_CATALOG
from backend.main import app


class TestBuyerProfilesCatalog:
    """Verifies empirical catalog correctness and data integrity."""

    def test_metadata_attributes(self):
        assert BUYER_MODEL_METADATA["total_historical_records"] == 2583
        assert BUYER_MODEL_METADATA["cluster_count"] == 5
        assert BUYER_MODEL_METADATA["evaluation_result"] == 0.7209
        assert BUYER_MODEL_METADATA["location_agnostic"] is True
        assert "location-agnostic" in BUYER_MODEL_METADATA["governance_notice"].lower()

    def test_overall_cohort_distribution(self):
        bhk_dist = OVERALL_BUYER_COHORT["configuration_distribution"]
        total_share = sum(bhk_dist.values())
        assert abs(total_share - 100.0) < 0.2
        assert bhk_dist["3BHK"] == 46.8
        assert bhk_dist["2BHK"] == 27.7
        assert bhk_dist["1BHK"] == 24.4
        assert bhk_dist["4BHK"] == 1.2

    def test_cluster_profiles_completeness(self):
        assert len(CLUSTER_PROFILES) == 5
        for cid, prof in CLUSTER_PROFILES.items():
            assert prof["cluster_id"] == cid
            assert "segment_name" in prof
            assert "dominant_industry" in prof
            assert prof["sample_size"] > 0
            assert prof["first_home_percentage"] > 90.0  # High first-home share across all reported cohorts
            assert "bhk_distribution" in prof
            assert abs(sum(prof["bhk_distribution"].values()) - 100.0) < 1.0

    def test_income_reporting_disclosure(self):
        inc = OVERALL_BUYER_COHORT["income_disclosure"]
        assert inc["reported_records"] == 198
        assert inc["reporting_rate_pct"] == 7.7
        assert "fabricate" in inc["disclosure_note"].lower()


class TestCategoricalAlignment:
    """Verifies objective categorical alignment logic and tier thresholds."""

    def test_canonical_bhk_parsing(self):
        assert get_canonical_bhk("3BHK") == "3BHK"
        assert get_canonical_bhk("3 BHK") == "3BHK"
        assert get_canonical_bhk("3") == "3BHK"
        assert get_canonical_bhk("2bhk") == "2BHK"
        assert get_canonical_bhk("1 BHK Grand") == "1BHK"
        assert get_canonical_bhk("4BHK Luxury") == "4BHK"
        assert get_canonical_bhk(None) == "2BHK"

    def test_strong_alignment(self):
        # 3BHK in Cluster 2 (Engineering) is 70.5% >= 50%
        res = evaluate_categorical_alignment("3BHK", 2)
        assert res["alignment_tier"] == "Strong Historical Alignment"
        assert res["alignment_code"] == "STRONG"
        assert res["segment_share_percentage"] == 70.5

    def test_moderate_alignment(self):
        # 3BHK in Cluster 0 (Tech/IT) is 39.9% in [20%, 50%)
        res = evaluate_categorical_alignment("3BHK", 0)
        assert res["alignment_tier"] == "Moderate Historical Alignment"
        assert res["alignment_code"] == "MODERATE"
        assert res["segment_share_percentage"] == 39.9

    def test_limited_alignment(self):
        # 2BHK in Cluster 2 (Engineering) is 15.9% in [1%, 20%)
        res = evaluate_categorical_alignment("2BHK", 2)
        assert res["alignment_tier"] == "Limited Historical Alignment"
        assert res["alignment_code"] == "LIMITED"
        assert res["segment_share_percentage"] == 15.9

    def test_insufficient_evidence(self):
        # 4BHK in Cluster 0 (Tech/IT) is 0.0% < 1%
        res = evaluate_categorical_alignment("4BHK", 0)
        assert res["alignment_tier"] == "Insufficient Evidence"
        assert res["alignment_code"] == "INSUFFICIENT"
        assert res["segment_share_percentage"] == 0.0

    def test_get_all_segment_alignments(self):
        alignments = get_all_segment_alignments("3BHK")
        assert len(alignments) == 5
        cluster_ids = [a["cluster_id"] for a in alignments]
        assert cluster_ids == [0, 1, 2, 3, 4]


class TestBuyerInference:
    """Verifies evaluate_buyer_fit function and backward compatibility."""

    def test_inference_success(self):
        fit = evaluate_buyer_fit(bhk_str="3BHK", property_segment="Mid", price_per_sqft=6500.0)
        assert fit["ml_used"] is True
        assert fit["model_version"] == "v1.2.0"
        assert fit["evaluation_result"] == 0.7209
        assert fit["predicted_cluster_id"] in [0, 1, 2, 3, 4]
        assert "primary_segment" in fit
        assert "categorical_alignment" in fit
        assert "overall_cohort" in fit
        assert len(fit["all_segment_alignments"]) == 5
        assert len(fit["evidence"]) >= 4
        assert len(fit["limitations"]) >= 2
        # Governance notice present
        assert "location-agnostic" in fit["governance_notice"].lower()

    def test_backward_compatibility_keys(self):
        fit = evaluate_buyer_fit(bhk_str="2BHK", property_segment="Mid", price_per_sqft=6000.0)
        required_legacy_keys = [
            "ml_used", "model_name", "evaluation_metric", "evaluation_result",
            "predicted_cluster_id", "primary_segment", "segment_share_percentage",
            "target_bhk", "preferred_cluster_bhk", "avg_household_income_lakhs",
            "first_home_percentage", "dominant_industry", "sample_size",
            "buyer_fit_index", "all_segments"
        ]
        for k in required_legacy_keys:
            assert k in fit, f"Missing legacy key: {k}"


class TestBuyerAgent:
    """Verifies BuyerAgent behavior and evidence structuring."""

    def test_buyer_agent_evaluation(self):
        agent = BuyerAgent()
        proj = ProjectInput(
            project_name="Purva Atmosphere Test",
            location="Thanisandra",
            micro_market="Thanisandra",
            price_per_sqft=7500.0,
            units=400,
            bhk="3BHK"
        )
        ev = agent.evaluate(proj)
        assert ev.agent_name == "Buyer Intelligence Agent"
        assert ev.status == "available"
        assert ev.ml_used is True
        assert ev.decision_bias in ["supportive", "neutral"]
        assert ev.confidence == 0.72
        assert "location-agnostic" in ev.summary.lower()
        assert any("location-agnostic" in lim.lower() for lim in ev.limitations)
        assert ev.metrics["target_bhk"] == "3BHK"
        assert "alignment_tier" in ev.metrics

    def test_buyer_agent_disabled(self):
        agent = BuyerAgent()
        proj = ProjectInput(
            project_name="Purva Disabled",
            location="Whitefield",
            micro_market="Whitefield",
            price_per_sqft=8000.0,
            units=200,
            include_buyer_intelligence=False
        )
        ev = agent.evaluate(proj)
        assert ev.status == "unavailable"
        assert ev.ml_used is False


class TestToolRegistryAndAPI:
    """Verifies Copilot tool execution and FastAPI endpoint."""

    def test_tool_catalog_registration(self):
        tool_names = [t["name"] for t in TOOL_CATALOG]
        assert "predict_buyer_segments" in tool_names
        assert "get_buyer_segments" in tool_names

    def test_execute_predict_buyer_segments(self):
        res = execute_tool("predict_buyer_segments", {
            "bhk_str": "3BHK",
            "property_segment": "Mid",
            "price_per_sqft": 6500.0,
            "units": 300
        })
        assert res["status"] == "success"
        assert res["data"]["ml_used"] is True
        assert res["data"]["target_bhk"] == "3BHK"
        assert any("location-agnostic" in lim.lower() for lim in res["limitations"])

    def test_fastapi_buyer_predict_endpoint(self):
        client = TestClient(app)
        response = client.post("/ml/buyer/predict", json={
            "bhk": "3BHK",
            "property_segment": "Mid",
            "price_per_sqft": 6500.0,
            "units": 300
        })
        assert response.status_code == 200
        data = response.json()
        assert data["ml_used"] is True
        assert data["target_bhk"] == "3BHK"
        assert "categorical_alignment" in data
        assert data["categorical_alignment"]["alignment_code"] in ["STRONG", "MODERATE", "LIMITED", "INSUFFICIENT"]
        assert "location-agnostic" in data["governance_notice"].lower()
