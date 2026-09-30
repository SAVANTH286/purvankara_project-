import json
import pytest
from backend.agents.base import ProjectInput
from backend.engine.scenario_engine import ScenarioEngine, ScenarioRequest
from backend.engine.decision_engine import DecisionEngine
from backend.db.connection import get_db
from backend.intelligence.tool_registry import run_scenario, AVAILABLE_TOOLS


@pytest.fixture
def sample_project():
    return ProjectInput(
        project_name="Purva Test Horizon",
        developer="Puravankara",
        property_type="Residential",
        property_segment="Mid",
        location="Kanakapura Road",
        micro_market="Kanakapura Road",
        price_per_sqft=6500.0,
        units=300,
        bhk="3BHK"
    )


def test_baseline_trajectory_and_conservation(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300,
        competitor_launch_month=4,
        intervention_month=6,
        intervention_price_adjustment_pct=-5.0,
        simulation_seed=42
    )
    res = engine.run_scenario(req)

    trajectory = res.get("monthly_trajectory", [])
    assert len(trajectory) == 12, "Trajectory must contain exactly 12 months"

    total_base_bookings = 0
    total_base_revenue = 0.0

    for row in trajectory:
        b_book = row["monthly_bookings_baseline"]
        b_rem = row["remaining_units_baseline"]
        b_rev = row["monthly_revenue_baseline"]

        assert b_book >= 0, f"Month {row['month']} bookings must be non-negative"
        assert b_rem >= 0, f"Month {row['month']} remaining units must be non-negative"
        assert b_rev >= 0.0, f"Month {row['month']} revenue must be non-negative"

        total_base_bookings += b_book
        total_base_revenue += b_rev

    assert total_base_bookings <= 300, "Cumulative bookings cannot exceed planned units"
    assert trajectory[-1]["cumulative_bookings_baseline"] == total_base_bookings
    assert abs(trajectory[-1]["cumulative_revenue_baseline"] - total_base_revenue) < 0.2


def test_blind_spot_trajectory_and_sales_drag(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300,
        competitor_launch_month=4,
        intervention_month=6,
        intervention_price_adjustment_pct=-5.0,
        simulation_seed=42
    )
    res = engine.run_scenario(req)

    trajectory = res.get("monthly_trajectory", [])
    # Months 1-3: Blind spot matches baseline
    for m in range(1, 4):
        row = trajectory[m - 1]
        assert row["monthly_bookings_blind_spot"] == row["monthly_bookings_baseline"], (
            f"Month {m} blind spot bookings should match baseline before competitor entry"
        )
        assert row["competition_active"] is False

    # Months 4-12: Competitor active, sales drag applied
    for m in range(4, 13):
        row = trajectory[m - 1]
        assert row["competition_active"] is True
        assert row["monthly_bookings_blind_spot"] <= row["monthly_bookings_baseline"]

    # Blind Spot Loss calculation
    blind_loss = res.get("blind_spot_loss_cr", 0.0)
    assert blind_loss > 0.0, f"Blind spot loss must be positive, got {blind_loss}"
    assert res["blind_spot"]["cumulative_revenue_cr"] < res["baseline"]["cumulative_revenue_cr"]


def test_competition_grounding_real_projects(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300
    )
    res = engine.run_scenario(req)

    comp = res.get("competition", {})
    assert comp.get("status") == "active_verified"
    assert comp.get("developer") is not None
    assert comp.get("project_name") is not None
    assert comp.get("price_per_sqft") > 0
    assert "Database" in comp.get("source", "")


def test_intervention_trajectory_and_recovery(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6800.0,
        new_units=300,
        competitor_launch_month=4,
        intervention_month=6,
        intervention_price_adjustment_pct=-5.0,
        simulation_seed=42
    )
    res = engine.run_scenario(req)

    recovery_cr = res.get("intervention_recovery_cr", 0.0)
    recovery_pct = res.get("recovery_percentage", 0.0)

    assert recovery_cr > 0.0, f"Intervention recovery must be positive, got {recovery_cr}"
    assert 0.0 <= recovery_pct <= 100.0, f"Recovery % must be bounded between 0 and 100, got {recovery_pct}"

    trajectory = res.get("monthly_trajectory", [])
    # Months 4-5: Intervention not active, matches blind spot
    for m in [4, 5]:
        row = trajectory[m - 1]
        assert row["intervention_active"] is False
        assert row["monthly_bookings_intervention"] == row["monthly_bookings_blind_spot"]

    # Month 6+: Intervention active
    for m in range(6, 13):
        row = trajectory[m - 1]
        assert row["intervention_active"] is True


def test_inventory_and_revenue_conservation(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=7000.0,
        new_units=250,
        competitor_launch_month=3,
        intervention_month=5,
        intervention_price_adjustment_pct=-7.0,
        simulation_seed=42
    )
    res = engine.run_scenario(req)
    trajectory = res.get("monthly_trajectory", [])

    for r in trajectory:
        # Inventory conservation
        assert r["monthly_bookings_baseline"] >= 0
        assert r["remaining_units_baseline"] >= 0
        assert r["cumulative_bookings_baseline"] <= 250

        assert r["monthly_bookings_blind_spot"] >= 0
        assert r["remaining_units_blind_spot"] >= 0
        assert r["cumulative_bookings_blind_spot"] <= 250

        assert r["monthly_bookings_intervention"] >= 0
        assert r["remaining_units_intervention"] >= 0
        assert r["cumulative_bookings_intervention"] <= 250

        # Revenue conservation
        assert r["monthly_revenue_baseline"] >= 0.0
        assert r["monthly_revenue_blind_spot"] >= 0.0
        assert r["monthly_revenue_intervention"] >= 0.0


def test_deterministic_seed_repeatability(sample_project):
    engine = ScenarioEngine()
    req1 = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300,
        simulation_seed=42
    )
    req2 = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300,
        simulation_seed=42
    )
    res1 = engine.run_scenario(req1)
    res2 = engine.run_scenario(req2)

    assert res1["blind_spot_loss_cr"] == res2["blind_spot_loss_cr"]
    assert res1["intervention_recovery_cr"] == res2["intervention_recovery_cr"]
    assert res1["recovery_percentage"] == res2["recovery_percentage"]
    assert res1["monthly_trajectory"] == res2["monthly_trajectory"]


def test_decision_engine_sole_authority_hurdles():
    de = DecisionEngine()
    # Launch: Abs >= 80, Margin >= 18, Risk < 55
    assert de.determine_verdict(85.0, 22.0, 40.0) == "Launch"
    # Hold: Abs >= 65, Margin >= 14, Risk < 70
    assert de.determine_verdict(70.0, 16.0, 60.0) == "Hold"
    # No-launch: below hurdles
    assert de.determine_verdict(50.0, 12.0, 75.0) == "No-launch"
    assert de.determine_verdict(85.0, 10.0, 40.0) == "No-launch"


def test_relational_database_traceability(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6600.0,
        new_units=300
    )
    res = engine.run_scenario(req)

    dec_id = res.get("decision_result_id")
    assert dec_id is not None, "Scenario run must produce a valid decision_result_id"

    with get_db() as db:
        # Check decision_results
        dec_row = db.query_one("SELECT * FROM decision_results WHERE id = %s", (dec_id,))
        assert dec_row is not None
        dec_dict = dict(dec_row)
        assert dec_dict["decision"] == res.get("decision")
        assert dec_dict["scenario_considered"] in [1, True]

        # Check decision_evidence
        ev_rows = db.query("SELECT * FROM decision_evidence WHERE decision_result_id = %s", (dec_id,))
        assert len(ev_rows) >= 5, "Must record granular evidence factors"

        # Check scenario_runs foreign link
        sr_row = db.query_one(
            "SELECT * FROM scenario_runs WHERE decision_result_id = %s ORDER BY id DESC LIMIT 1",
            (dec_id,)
        )
        assert sr_row is not None
        assert dict(sr_row)["decision_result_id"] == dec_id


def test_cannibalization_explicitly_labeled_as_assumption(sample_project):
    engine = ScenarioEngine()
    req = ScenarioRequest(
        base_project=sample_project,
        new_price_per_sqft=6500.0,
        new_units=300
    )
    res = engine.run_scenario(req)

    assumptions = res["scenario_evidence"]["assumptions"]
    cannibalization_text = assumptions.get("competitor_cannibalization_effect", "")
    assert "SCENARIO ASSUMPTION" in cannibalization_text
    assert "NOT an empirically validated" in cannibalization_text

    how_calc = res["how_calculated"]
    competitor_metric = [m for m in how_calc if "Competitor" in m["metric"]][0]
    assert "[DATABASE + SCENARIO ASSUMPTION]" in competitor_metric["source"]


def test_copilot_tool_registry_run_scenario_schema_and_call():
    # Verify tool in AVAILABLE_TOOLS
    tool_def = [t for t in AVAILABLE_TOOLS if t["name"] == "run_scenario"]
    assert len(tool_def) == 1
    props = tool_def[0]["parameters"]["properties"]
    assert "competitor_launch_month" in props
    assert "intervention_month" in props
    assert "intervention_price_adjustment_pct" in props

    # Execute tool
    result = run_scenario({
        "micro_market": "Kanakapura Road",
        "base_price_per_sqft": 6500.0,
        "base_units": 300,
        "new_price_per_sqft": 6700.0,
        "competitor_launch_month": 4,
        "intervention_month": 6
    })

    assert result["status"] == "success"
    data = result["data"]
    assert "decision" in data
    assert "baseline" in data
    assert "blind_spot" in data
    assert "competition" in data
    assert "intervention" in data
    assert "monthly_trajectory" in data
    assert len(data["monthly_trajectory"]) == 12
