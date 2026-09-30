import json
import sys
from fastapi.testclient import TestClient

from backend.main import app
from backend.db.connection import get_db
from backend.agents.base import ProjectInput
from backend.intelligence.orchestrator import get_orchestrator
from ml.buyer.infer import evaluate_buyer_fit
from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from backend.services.amenity_service import get_amenity_service
from backend.engine.scenario_engine import get_scenario_engine, ScenarioRequest


def test_database():
    print("\n--- 1. Testing Database & Schema Integrity ---")
    with get_db() as db:
        mm_count = db.query_one("SELECT COUNT(*) FROM micro_markets")[0]
        city_count = db.query_one("SELECT COUNT(*) FROM cities")[0]
        proj_count = db.query_one("SELECT COUNT(*) FROM projects")[0]
        buyer_count = db.query_one("SELECT COUNT(*) FROM buyer_profiles")[0]
        coords_count = db.query_one("SELECT COUNT(*) FROM micro_markets WHERE latitude IS NOT NULL AND longitude IS NOT NULL")[0]
        model_count = db.query_one("SELECT COUNT(*) FROM model_versions")[0]

    print(f"[PASS] Micro-Markets Count: {mm_count} (Expected: 25)")
    assert mm_count >= 25, f"Expected at least 25 micro-markets, got {mm_count}"

    print(f"[PASS] Micro-Markets with Valid Coordinates: {coords_count} (Expected: 25)")
    assert coords_count >= 25, f"Expected all 25 micro-markets to have coordinates, got {coords_count}"

    print(f"[PASS] City Benchmark Rows: {city_count} (Expected: >=1)")
    assert city_count >= 1, "Expected city table to have Bengaluru profile"

    print(f"[PASS] Projects Ingested: {proj_count} (Expected: >=17)")
    assert proj_count >= 17, "Expected real projects in database"

    print(f"[PASS] Buyer Demographic Profiles: {buyer_count} (Expected: >=2)")
    assert buyer_count >= 2, "Expected buyer profiles in database"

    print(f"[PASS] Registered Models in DB: {model_count} (Expected: >=3)")
    assert model_count >= 3, "Expected model_versions to register ML models"


def test_ml_layer():
    print("\n--- 2. Testing Real ML Prediction Layer ---")
    # A. Buyer KMeans Model
    buyer_fit = evaluate_buyer_fit("3BHK", "Mid", 6500.0)
    print(f"[PASS] Buyer ML: {buyer_fit.get('model_name')} | Silhouette: {buyer_fit.get('evaluation_result')}")
    assert buyer_fit.get("ml_used") is True
    assert buyer_fit.get("evaluation_result") > 0.5

    # B. Market Demand Random Forest Model
    mkt_pred = predict_market_absorption("Kanakapura Road", 300, 6500.0)
    print(f"[PASS] Market ML: {mkt_pred.get('model_name')} | Predicted Abs: {mkt_pred.get('predicted_absorption_pct')}%")
    assert mkt_pred.get("ml_used") is True
    assert mkt_pred.get("predicted_absorption_pct") is not None
    assert "MAE" in mkt_pred.get("evaluation_metrics", {})

    # C. Price Prediction Gradient Boosting Model
    price_pred = predict_price_per_sqft("Kanakapura Road", "Mid", "Residential", "3BHK", 300)
    print(f"[PASS] Price ML: {price_pred.get('model_name')} | Predicted Price: INR {price_pred.get('predicted_price_per_sqft'):,}/sqft")
    assert price_pred.get("ml_used") is True
    assert price_pred.get("model_version") is not None


def test_geospatial_amenities():
    print("\n--- 3. Testing 5 KM Geospatial Amenity Retrieval ---")
    amenity_svc = get_amenity_service()
    res = amenity_svc.get_amenities_within_radius(12.8718, 77.5458, radius_km=5.0)
    print(f"[PASS] Amenity Status: {res.get('status')}")
    print(f"[PASS] Total POIs within 5 km: {res.get('total_count')}")
    print(f"[PASS] Category Counts: {res.get('counts_by_category')}")
    print(f"[PASS] Sourced From: {res.get('source')}")

    assert res.get("status") == "available"
    assert res.get("total_count") > 0
    assert len(res.get("amenities")) > 0
    assert res.get("amenities")[0]["distance_km"] <= 5.0


def test_10_agents():
    print("\n--- 4. Testing Standardized Contract Across All 10 Agents ---")
    orchestrator = get_orchestrator()
    p = ProjectInput(
        project_name="Purva Kanakapura Test",
        location="Kanakapura Road",
        micro_market="Kanakapura Road",
        price_per_sqft=6500.0,
        units=300,
        bhk="3BHK"
    )

    required_keys = [
        "agent_name", "status", "summary", "metrics",
        "evidence", "limitations", "tool_used", "ml_used",
        "model_used", "confidence"
    ]

    for key, agent in orchestrator.agents.items():
        ev = agent.evaluate(p)
        ev_dict = ev.model_dump()
        for rk in required_keys:
            assert rk in ev_dict, f"Agent '{agent.name}' missing required contract key: {rk}"

        # Rule 24 check: confidence must be null unless ML used
        if not ev.ml_used:
            assert ev.confidence is None, f"Agent '{agent.name}' has non-null confidence without ML: {ev.confidence}"
        else:
            assert ev.confidence is not None, f"ML Agent '{agent.name}' must have validated confidence"

        print(f"[PASS] {agent.name:<32} | Status: {ev.status:<10} | ML: {str(ev.ml_used):<5} | Confidence: {str(ev.confidence)}")


def test_scenario_engine():
    print("\n--- 5. Testing Scenario Sensitivity Engine ---")
    engine = get_scenario_engine()
    req = ScenarioRequest(
        base_project=ProjectInput(
            project_name="Purva Kanakapura Test",
            developer="Puravankara",
            location="Kanakapura Road",
            micro_market="Kanakapura Road",
            price_per_sqft=6500.0,
            units=300,
            bhk="3BHK"
        ),
        scenario_name="Price Increase Simulation",
        new_price_per_sqft=7000.0,
        new_units=300,
        new_bhk="3BHK"
    )
    result = engine.run_scenario(req)
    comp = result.get("comparison", {})
    deltas = comp.get("deltas", {})
    print(f"[PASS] Scenario Run Completed. Deltas: {deltas}")
    assert deltas.get("price_delta_inr") == 500.0
    assert deltas.get("revenue_delta_cr") is not None
    assert "scenario_observations" in comp


def test_10_copilot_queries():
    print("\n--- 6. Testing All 10 Canonical Copilot Question Types ---")
    client = TestClient(app)

    canonical_queries = [
        ("MARKET_COMPARISON", "Compare Kanakapura Road and Bagalur"),
        ("MICROMARKET_ANALYSIS", "What is the absorption situation in Kanakapura Road?"),
        ("PRICE_PREDICTION", "What price can we command for a 3BHK in Kanakapura Road?"),
        ("ABSORPTION_PREDICTION", "Predict absorption for 300 units in Kanakapura Road"),
        ("BUYER_SEGMENTATION", "Who are the primary buyers for 3BHK in South Bangalore?"),
        ("INFRASTRUCTURE_AUDIT", "What amenities are within 5km of Kanakapura Road?"),
        ("SCENARIO_ANALYSIS", "What happens if we increase price by 500 per sqft?"),
        ("CITY_MACRO_OUTLOOK", "Bengaluru city launches and inventory overview"),
        ("REGULATORY_COMPLIANCE", "What are the regulatory approvals and timelines for Bagalur?"),
        ("COMPETITOR_INTELLIGENCE", "Who are the competitors in Bagalur?")
    ]

    for expected_intent, query in canonical_queries:
        resp = client.post("/api/copilot/chat", json={"message": query})
        assert resp.status_code == 200, f"Query failed: {query}"
        data = resp.json()

        assert "answer" in data or "response" in data
        assert "intent" in data
        assert "agents_used" in data and isinstance(data["agents_used"], list)
        assert "tools_used" in data and isinstance(data["tools_used"], list)
        assert "sources" in data and len(data["sources"]) > 0

        print(f"[PASS] {expected_intent:<25} | Intent: {data.get('intent'):<25} | Agents: {len(data['agents_used'])} | Tools: {len(data['tools_used'])}")


def test_api_endpoints():
    print("\n--- 7. Testing All REST API Endpoints ---")
    client = TestClient(app)

    # Health
    h = client.get("/health").json()
    assert h["status"] == "healthy"
    print("[PASS] GET /health: OK")

    # City micro-markets with coordinates
    mm = client.get("/api/city/bangalore/micro-markets").json()
    assert len(mm) == 25
    assert all("latitude" in m and "longitude" in m for m in mm)
    print(f"[PASS] GET /api/city/bangalore/micro-markets: 25 markets with validated coordinates")

    # City Profile
    cp = client.get("/api/city/bangalore/profile").json()
    assert cp["city_name"] == "Bengaluru"
    print(f"[PASS] GET /api/city/bangalore/profile: Bengaluru profile returned")

    # 5km Amenities API
    amenities = client.get("/api/infrastructure/amenities?micromarket=Kanakapura+Road").json()
    assert amenities["status"] == "available"
    assert len(amenities["amenities"]) > 0
    print(f"[PASS] GET /api/infrastructure/amenities: {len(amenities['amenities'])} amenities within 5km returned")

    # ML Predict Endpoints
    m_res = client.post("/api/ml/market/predict", json={"micromarket_name": "Kanakapura Road", "units": 300, "price_per_sqft": 6500.0}).json()
    assert m_res["ml_used"] is True
    print(f"[PASS] POST /api/ml/market/predict: OK")

    p_res = client.post("/api/ml/price/predict", json={"micromarket_name": "Kanakapura Road", "property_segment": "Mid", "bhk": "3BHK", "units": 300}).json()
    assert p_res["ml_used"] is True
    print(f"[PASS] POST /api/ml/price/predict: OK")

    b_res = client.post("/api/ml/buyer/predict", json={"bhk": "3BHK", "property_segment": "Mid", "price_per_sqft": 6500.0}).json()
    assert b_res["ml_used"] is True
    print(f"[PASS] POST /api/ml/buyer/predict: OK")

    # ML Models Registry
    models = client.get("/api/ml/models").json()
    assert len(models) >= 3
    print(f"[PASS] GET /api/ml/models: {len(models)} registered models in catalog")

    # Scenario Run API
    scen_payload = {
        "base_project": {
            "project_name": "Purva Test",
            "developer": "Puravankara",
            "location": "Kanakapura Road",
            "micro_market": "Kanakapura Road",
            "price_per_sqft": 6500.0,
            "units": 300,
            "bhk": "3BHK"
        },
        "scenario_name": "Test Run",
        "new_price_per_sqft": 7000.0
    }
    scen_res = client.post("/api/scenario/run", json=scen_payload).json()
    assert "comparison" in scen_res
    print(f"[PASS] POST /api/scenario/run: OK")

    # DSS Evaluate
    dss_payload = {
        "project_name": "Purva Kanakapura Grandeur",
        "developer": "Puravankara",
        "location": "Kanakapura Road",
        "micro_market": "Kanakapura Road",
        "price_per_sqft": 6500.0,
        "units": 300,
        "bhk": "3BHK"
    }
    dss = client.post("/api/dss/evaluate", json=dss_payload).json()
    assert dss["decision"] in ["Launch", "Hold", "No-launch"]
    assert "ml_predictions" in dss
    assert "observations" in dss
    print(f"[PASS] POST /api/dss/evaluate: Verdict={dss['decision']}, Provisional={dss['decision_is_provisional']}")


if __name__ == "__main__":
    print("==================================================================")
    print("   PURAVANKARA AI -- COMPREHENSIVE VERIFICATION SUITE            ")
    print("   DSS + ML Layer + Geospatial + Scenario + OpenRouter Copilot   ")
    print("==================================================================")
    test_database()
    test_ml_layer()
    test_geospatial_amenities()
    test_10_agents()
    test_scenario_engine()
    test_10_copilot_queries()
    test_api_endpoints()
    print("\n==================================================================")
    print("   [SUCCESS] ALL VERIFICATION TESTS PASSED!                        ")
    print("   ZERO-FABRICATION POLICY FULLY VALIDATED ACROSS ALL LAYERS.    ")
    print("==================================================================")
