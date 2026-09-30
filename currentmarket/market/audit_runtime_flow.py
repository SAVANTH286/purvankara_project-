import json
import pandas as pd
from ml.market.infer import load_model, predict_market_absorption
from backend.agents.base import ProjectInput
from backend.agents.finance_agent import FinanceAgent
from backend.engine.risk_engine import RiskEngine
from backend.intelligence.orchestrator import get_orchestrator

print("=========================================================")
print("1. AUDIT: MARKET DEMAND ML INFERENCE & FEATURES")
print("=========================================================")

model_data = load_model()
model = model_data["model"]
scaler = model_data["scaler"]
feature_cols = model_data["feature_cols"]

print("Model features:", feature_cols)
print("Model algorithm:", model_data.get("algorithm"))

# Base: units = 300
base_input_dict = {
    "unsold_units": 800.0,
    "overhang_months": 4.5,
    "total_available": 300.0 + 800.0 # 1100.0
}
base_df = pd.DataFrame([base_input_dict])[feature_cols]
base_scaled = scaler.transform(base_df)
raw_base_pred = float(model.predict(base_scaled)[0])
base_pred_dict = predict_market_absorption("Kanakapura Road", 300, 6500)

print(f"BASE: input={base_input_dict}")
print(f"BASE: scaled vector={base_scaled[0]}")
print(f"BASE: raw model prediction={raw_base_pred}")
print(f"BASE: returned predicted_absorption_pct={base_pred_dict.get('predicted_absorption_pct')}")

# Scenario: units = 370
scen_input_dict = {
    "unsold_units": 800.0,
    "overhang_months": 4.5,
    "total_available": 370.0 + 800.0 # 1170.0
}
scen_df = pd.DataFrame([scen_input_dict])[feature_cols]
scen_scaled = scaler.transform(scen_df)
raw_scen_pred = float(model.predict(scen_scaled)[0])
scen_pred_dict = predict_market_absorption("Kanakapura Road", 370, 7200)

print(f"\nSCENARIO: input={scen_input_dict}")
print(f"SCENARIO: scaled vector={scen_scaled[0]}")
print(f"SCENARIO: raw model prediction={raw_scen_pred}")
print(f"SCENARIO: returned predicted_absorption_pct={scen_pred_dict.get('predicted_absorption_pct')}")

# Check what the model predicts across various total_available values
print("\n--- MODEL SENSITIVITY CURVE ON TOTAL_AVAILABLE ---")
for test_units in [50, 100, 200, 300, 370, 500, 800, 1500, 3000, 5000]:
    t_dict = {"unsold_units": 800.0, "overhang_months": 4.5, "total_available": test_units + 800.0}
    t_df = pd.DataFrame([t_dict])[feature_cols]
    t_scaled = scaler.transform(t_df)
    t_raw = float(model.predict(t_scaled)[0])
    t_clipped = max(35.0, min(98.5, round(t_raw, 2)))
    print(f"Units={test_units:4d} | total_avail={test_units+800:5.0f} | raw={t_raw:7.2f}% | clipped={t_clipped:5.1f}%")

print("\n=========================================================")
print("2. AUDIT: REVENUE & SALEABLE AREA CALCULATIONS")
print("=========================================================")

fa = FinanceAgent()

# Base with 3BHK:
p_base_3bhk = ProjectInput(
    project_name="Base 3BHK",
    developer="Puravankara",
    property_type="Residential",
    property_segment="Mid",
    location="Kanakapura Road",
    micro_market="Kanakapura Road",
    price_per_sqft=6500.0,
    units=300,
    bhk="3BHK"
)
ev_base_3bhk = fa.evaluate(p_base_3bhk)
m_b3 = ev_base_3bhk.metrics

# Base with 2BHK:
p_base_2bhk = ProjectInput(
    project_name="Base 2BHK",
    developer="Puravankara",
    property_type="Residential",
    property_segment="Mid",
    location="Kanakapura Road",
    micro_market="Kanakapura Road",
    price_per_sqft=6500.0,
    units=300,
    bhk="2BHK"
)
ev_base_2bhk = fa.evaluate(p_base_2bhk)
m_b2 = ev_base_2bhk.metrics

# Scenario with 1BHK:
p_scen_1bhk = ProjectInput(
    project_name="Scenario 1BHK",
    developer="Puravankara",
    property_type="Residential",
    property_segment="Mid",
    location="Kanakapura Road",
    micro_market="Kanakapura Road",
    price_per_sqft=7200.0,
    units=370,
    bhk="1BHK"
)
ev_scen_1bhk = fa.evaluate(p_scen_1bhk)
m_s1 = ev_scen_1bhk.metrics

print(f"BASE (3BHK, 300 units, 6500/sqft):")
print(f"  Avg sqft = 1,450 sq.ft")
print(f"  Saleable area = {m_b3['saleable_area_sqft']:,} sq.ft")
print(f"  Gross revenue = INR {m_b3['gross_revenue_cr']} Cr")
print(f"  Gross margin = {m_b3['gross_margin_pct']}%")

print(f"\nBASE (2BHK, 300 units, 6500/sqft):")
print(f"  Avg sqft = 1,050 sq.ft")
print(f"  Saleable area = {m_b2['saleable_area_sqft']:,} sq.ft")
print(f"  Gross revenue = INR {m_b2['gross_revenue_cr']} Cr")
print(f"  Gross margin = {m_b2['gross_margin_pct']}%")

print(f"\nSCENARIO (1BHK, 370 units, 7200/sqft):")
print(f"  Avg sqft = 650 sq.ft")
print(f"  Saleable area = {m_s1['saleable_area_sqft']:,} sq.ft")
print(f"  Gross revenue = INR {m_s1['gross_revenue_cr']} Cr")
print(f"  Gross margin = {m_s1['gross_margin_pct']}%")

print(f"\nREVENUE DELTA IF BASE WAS 3BHK: {m_s1['gross_revenue_cr']} - {m_b3['gross_revenue_cr']} = {round(m_s1['gross_revenue_cr'] - m_b3['gross_revenue_cr'], 2)} Cr")
print(f"REVENUE DELTA IF BASE WAS 2BHK: {m_s1['gross_revenue_cr']} - {m_b2['gross_revenue_cr']} = {round(m_s1['gross_revenue_cr'] - m_b2['gross_revenue_cr'], 2)} Cr")

print("\n=========================================================")
print("3. AUDIT: RISK ENGINE RECALCULATION")
print("=========================================================")

orch = get_orchestrator()
base_eval_3bhk = orch.evaluate_project(p_base_3bhk)
base_eval_2bhk = orch.evaluate_project(p_base_2bhk)
scen_eval_1bhk = orch.evaluate_project(p_scen_1bhk)

print("Base 3BHK Risk Breakdown:", base_eval_3bhk["risk_assessment"]["breakdown"])
print("Base 3BHK Composite Risk:", base_eval_3bhk["risk_assessment"]["composite_risk_score"])
print("Base 2BHK Risk Breakdown:", base_eval_2bhk["risk_assessment"]["breakdown"])
print("Base 2BHK Composite Risk:", base_eval_2bhk["risk_assessment"]["composite_risk_score"])
print("Scen 1BHK Risk Breakdown:", scen_eval_1bhk["risk_assessment"]["breakdown"])
print("Scen 1BHK Composite Risk:", scen_eval_1bhk["risk_assessment"]["composite_risk_score"])
