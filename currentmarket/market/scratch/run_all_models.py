import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from ml.buyer.infer import evaluate_buyer_fit
from backend.agents.base import ProjectInput
from backend.dss_api import evaluate_project
from backend.engine.scenario_engine import ScenarioEngine, ScenarioRequest

print("=" * 68)
print("       PURAVANKARA AI DECISION SUPPORT SYSTEM — MODEL EXECUTION")
print("=" * 68)

# 1. Market Demand ML Model (Random Forest Regressor)
print("\n[MODEL 1] Market Demand & Absorption ML Model (Random Forest)")
print("-" * 68)
m = predict_market_absorption(
    micromarket_name="Kanakapura Road",
    units=300,
    price_per_sqft=6500.0
)
print(f"  * Corridor Evaluated : Kanakapura Road (300 Units @ Rs.6,500/sq.ft)")
print(f"  * Algorithm          : {m.get('algorithm', 'RandomForestRegressor')}")
print(f"  * R2 Score / MAE     : R2 = {m['evaluation_metrics']['R2_Score']} | MAE = {m['evaluation_metrics']['MAE']}%")
print(f"  * Predicted Absorption: {m['predicted_absorption_pct']}% ({m['predicted_absorbed_units']} / {m['planned_units']} units)")

# 2. Price Prediction ML Model (Gradient Boosting Regressor)
print("\n[MODEL 2] Realization Price Prediction ML Model (Gradient Boosting)")
print("-" * 68)
p = predict_price_per_sqft(
    micromarket_name="Kanakapura Road",
    property_segment="Mid",
    property_type="Residential",
    bhk_str="3BHK",
    units=300
)
print(f"  * Corridor & Segment : Kanakapura Road | Mid Segment | 3BHK | 300 units")
print(f"  * Algorithm          : {p.get('algorithm', 'GradientBoostingRegressor')}")
print(f"  * R2 Score / MAE     : R2 = {p['evaluation_metrics'].get('R2_Score')} | MAE = Rs.{p['evaluation_metrics'].get('MAE_INR_sqft')}/sq.ft")
print(f"  * Market Clearing Price: Rs.{p['predicted_price_per_sqft']:,.0f} / sq.ft")

# 3. Buyer Clustering ML Model (KMeans Demographic Clustering)
print("\n[MODEL 3] Buyer Persona & Demographic Clustering ML Model (KMeans)")
print("-" * 68)
b = evaluate_buyer_fit(
    bhk_str="3BHK",
    property_segment="Mid",
    price_per_sqft=6500.0
)
print(f"  * Training Dataset   : 2,583 verified customer bookings across Atmosphere, Blubelle, Ecopolitan")
print(f"  * Matched Persona    : {b['primary_segment']}")
print(f"  * Silhouette Score   : {b['evaluation_result']}")
print(f"  * Buyer Fit Index    : {b['buyer_fit_index']} / 1.00")
print(f"  * First-Home Propensity: {b.get('first_home_percentage')}% | Dominant Industry: {b.get('dominant_industry')}")

# 4. Multi-Agent Decision Support System (DSS Hurdle Evaluation)
print("\n[MODEL 4] DSS Multi-Agent Evaluation & Investment Hurdle Engine")
print("-" * 68)
proj = ProjectInput(
    project_name="Purva Kanakapura Launch Test",
    developer="Puravankara",
    property_type="Residential",
    property_segment="Mid",
    location="Kanakapura Road",
    micro_market="Kanakapura Road",
    price_per_sqft=6500.0,
    units=300,
    bhk="3BHK",
    launch_date="2026-10-01",
    include_buyer_intelligence=True
)
dss = evaluate_project(proj)
print(f"  * Official Verdict   : [{dss['decision'].upper()}]")
print(f"  * Composite Risk Score: {dss['risk_assessment']['composite_risk_score']} / 100 ({dss['risk_assessment']['risk_level']} Risk)")
print(f"  * Executive Summary  : {dss['executive_summary']}")

# 5. Canonical Scenario Engine (12-Month Simulation Matrix)
print("\n[MODEL 5] Canonical Scenario Engine (4 Dimensions + Trajectory Matrix)")
print("-" * 68)
engine = ScenarioEngine()
req = ScenarioRequest(
    base_project=proj,
    new_price_per_sqft=6500.0,
    new_units=300,
    competitor_launch_month=4,
    intervention_month=6,
    intervention_price_adjustment_pct=-5.0,
    simulation_seed=42
)
s = engine.run_scenario(req)
print(f"  * Baseline Revenue (12m)   : Rs.{s['baseline']['cumulative_revenue_cr']} Cr ({s['baseline']['total_bookings']} units booked / {s['baseline']['absorption_rate_pct']}%)")
print(f"  * Blind Spot Revenue Loss : Rs.{s['blind_spot']['blind_spot_revenue_loss_cr']} Cr (Bookings dropped to {s['blind_spot']['total_bookings']} units)")
print(f"  * Intervention Recovery   : Rs.{s['intervention']['intervention_recovery_cr']} Cr ({s['intervention']['recovery_percentage']}% recovered via -5% price adjustment)")
print(f"  * Official Scenario Verdict: [{s['decision']}] (Audit ID: {s['decision_result_id']})")
last_m = s['monthly_trajectory'][-1]
base_conserved = (last_m['cumulative_bookings_baseline'] + last_m['remaining_units_baseline'] == 300)
bs_conserved = (last_m['cumulative_bookings_blind_spot'] + last_m['remaining_units_blind_spot'] == 300)
int_conserved = (last_m['cumulative_bookings_intervention'] + last_m['remaining_units_intervention'] == 300)
print(f"  * Trajectory Conservation : {len(s['monthly_trajectory'])} monthly periods | Inventory Conserved across Baseline, Blind Spot & Intervention = {base_conserved and bs_conserved and int_conserved}")

print("\n" + "=" * 68)
print("               ALL 5 MODELS EXECUTED SUCCESSFULLY")
print("=" * 68)
