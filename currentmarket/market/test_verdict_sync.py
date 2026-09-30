import sys
import requests
from backend.engine.decision_engine import DecisionEngine

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_user_cases():
    print("==================================================================")
    print("TESTING 5 UNIT TEST CASES FOR DECISION ENGINE THRESHOLDS")
    print("==================================================================")
    # Case 1: Absorption 90%, Margin 22%, Risk 20 -> LAUNCH
    c1 = DecisionEngine.determine_verdict(90.0, 22.0, 20.0)
    assert c1 == "Launch", f"Case 1 failed: expected Launch, got {c1}"
    print(f"[PASS] Case 1: Absorption 90%, Margin 22%, Risk 20 -> {c1}")

    # Case 2: Absorption 70%, Margin 20%, Risk 30 -> HOLD
    c2 = DecisionEngine.determine_verdict(70.0, 20.0, 30.0)
    assert c2 == "Hold", f"Case 2 failed: expected Hold, got {c2}"
    print(f"[PASS] Case 2: Absorption 70%, Margin 20%, Risk 30 -> {c2}")

    # Case 3: Absorption 35%, Margin 19.8%, Risk 26.9 -> NO-LAUNCH
    c3 = DecisionEngine.determine_verdict(35.0, 19.8, 26.9)
    assert c3 == "No-launch", f"Case 3 failed: expected No-launch, got {c3}"
    print(f"[PASS] Case 3: Absorption 35%, Margin 19.8%, Risk 26.9 -> {c3}")

    # Case 4: Absorption 70%, Margin 12%, Risk 30 -> NO-LAUNCH
    c4 = DecisionEngine.determine_verdict(70.0, 12.0, 30.0)
    assert c4 == "No-launch", f"Case 4 failed: expected No-launch, got {c4}"
    print(f"[PASS] Case 4: Absorption 70%, Margin 12%, Risk 30 -> {c4}")

    # Case 5: Absorption 70%, Margin 20%, Risk 75 -> NO-LAUNCH
    c5 = DecisionEngine.determine_verdict(70.0, 20.0, 75.0)
    assert c5 == "No-launch", f"Case 5 failed: expected No-launch, got {c5}"
    print(f"[PASS] Case 5: Absorption 70%, Margin 20%, Risk 75 -> {c5}")

    print("\n==================================================================")
    print("TESTING END-TO-END SCENARIO API WITH USER'S BUG CASE (PRICE = 6400)")
    print("==================================================================")
    base_project = {
        "project_name": "Purva Kanakapura Grandeur",
        "developer": "Puravankara",
        "property_type": "Residential",
        "property_segment": "Mid",
        "location": "Kanakapura Road",
        "micro_market": "Kanakapura Road",
        "price_per_sqft": 6500.0,
        "units": 300,
        "bhk": "3BHK",
        "launch_date": "2026-10-01",
        "include_buyer_intelligence": True
    }

    payload = {
        "base_project": base_project,
        "scenario_name": "Price 6400 Test",
        "new_price_per_sqft": 6400.0,
        "new_units": 300,
        "new_bhk": "3BHK"
    }

    res = requests.post(f"{BASE_URL}/api/scenario/run", json=payload, timeout=10)
    assert res.status_code == 200, f"API failed with {res.status_code}: {res.text}"
    data = res.json()

    scen = data["scenario"]
    sim_abs = data["simulated_absorption_rate_pct"]
    sim_margin = scen["gross_margin_pct"]
    sim_risk = scen["composite_risk_score"]
    scen_decision = scen["decision"]
    comp_decision = data["comparison"]["scenario"]["decision"]
    eval_decision = data["scenario_evaluation"]["decision"]

    print(f"Scenario Price: INR {scen['price_per_sqft']}")
    print(f"Scenario Units: {scen['units']}")
    print(f"Scenario Gross Margin: {sim_margin}%")
    print(f"Scenario Absorption: {sim_abs}%")
    print(f"Scenario Risk: {sim_risk}/100")
    print(f"Scenario Verdict (scenario.decision): {scen_decision}")
    print(f"Scenario Verdict (comparison.scenario.decision): {comp_decision}")
    print(f"Scenario Verdict (scenario_evaluation.decision): {eval_decision}")

    assert scen_decision == comp_decision == eval_decision, f"Desynchronized verdicts: {scen_decision} vs {comp_decision} vs {eval_decision}"

    # Also test an aggressive price scenario (e.g. INR 11,500) that triggers No-launch
    payload_high = {
        "base_project": base_project,
        "scenario_name": "Price 11500 Test",
        "new_price_per_sqft": 11500.0,
        "new_units": 300,
        "new_bhk": "3BHK"
    }
    res_high = requests.post(f"{BASE_URL}/api/scenario/run", json=payload_high, timeout=10)
    assert res_high.status_code == 200
    data_high = res_high.json()
    scen_high = data_high["scenario"]
    assert scen_high["decision"] == "No-launch", f"Expected No-launch for INR 11,500, got {scen_high['decision']}"
    assert data_high["comparison"]["scenario"]["decision"] == "No-launch"
    assert data_high["scenario_evaluation"]["decision"] == "No-launch"

    # Verify how_calculated
    how_calc = data_high.get("how_calculated", [])
    verdict_row = next((r for r in how_calc if r.get("metric") == "Decision Verdict"), None)
    print(f"High Price How Calculated Verdict Row: {verdict_row}")
    assert verdict_row is not None
    assert "No-launch" in verdict_row["value"]

    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")
    return True

if __name__ == "__main__":
    success = test_user_cases()
    sys.exit(0 if success else 1)
