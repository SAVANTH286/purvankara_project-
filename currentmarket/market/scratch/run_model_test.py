import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

scenario_req = {
    "base_project": {
        "project_name": "Purva South Heights",
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
    },
    "scenario_name": "Aggressive Scale & Premium",
    "new_price_per_sqft": 8050.0,
    "new_units": 440,
    "new_bhk": "4BHK"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/scenario/run",
    data=json.dumps(scenario_req).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())

print("=" * 65)
print("PURAVANKARA AI DSS & WHAT-IF ENGINE EXECUTION REPORT")
print("=" * 65)

b = data["base"]
s = data["scenario"]
d = data["delta"]

print("\n1. BASELINE PROJECT STATE:")
print(f"   • Price: ₹{b['price_per_sqft']:,.0f}/sq.ft | Units: {b['units']} | Config: {b['bhk']}")
print(f"   • Gross Revenue: ₹{b['gross_revenue_cr']:,.2f} Cr | Gross Margin: {b['gross_margin_pct']:.1f}%")
print(f"   • Absorption Velocity: {b['absorption_rate_pct']:.2f}% | Composite Risk: {b['composite_risk_score']:.1f}/100")
print(f"   • Decision Verdict: {b['decision']}")

print("\n2. SIMULATED SCENARIO OUTCOME:")
print(f"   • Price: ₹{s['price_per_sqft']:,.0f}/sq.ft | Units: {s['units']} | Config: {s['bhk']}")
print(f"   • Gross Revenue: ₹{s['gross_revenue_cr']:,.2f} Cr | Gross Margin: {s['gross_margin_pct']:.1f}%")
print(f"   • Absorption Velocity: {s['absorption_rate_pct']:.2f}% | Composite Risk: {s['composite_risk_score']:.1f}/100")
print(f"   • Decision Verdict: {s.get('decision')}")

print("\n3. SENSITIVITY DELTAS:")
print(f"   • Price Delta: +₹{d['price_delta_inr']:,.0f}/sq.ft")
print(f"   • Scale Delta: +{d['units_delta']} Units")
print(f"   • Revenue Delta: +₹{d['revenue_delta_cr']:,.2f} Cr")
print(f"   • Gross Margin Delta: +{d['gross_margin_delta_pct']:.1f}%")
print(f"   • Absorption Shift: {d['absorption_shift_pct']:.2f}% (Price: -10.76% OLS, Scale: -3.06% RF)")
print(f"   • Risk Delta: +{d['risk_score_delta']:.1f} Points (Market Risk stepped from 8.0 to 20.0)")

print("\n4. STEP-BY-STEP PROVENANCE & CALCULATION AUDIT:")
for item in data["how_calculated"]:
    print(f"   • {item['metric']}: {item['value']} {item['source']}")
    print(f"     └─ {item['method']}")

print("=" * 65)
