from backend.agents.base import ProjectInput
from backend.dss_api import evaluate_project

# Boundary Case 1: Subdued market / High price / Low margin -> should trigger HOLD or NO-LAUNCH
boundary_payload = ProjectInput(
    project_name="High Risk Experimental Project",
    developer="Puravankara",
    property_type="Residential",
    property_segment="Mid",
    location="Peripheral Boundary",
    micro_market="Attibele-Chandapur",
    price_per_sqft=3500.0,  # Below construction cost + land cost -> negative/compressed margin!
    units=500,
    bhk="4BHK",
    launch_date="2026-10-01",
    include_buyer_intelligence=False
)

res = evaluate_project(boundary_payload)
print("Boundary Decision:", res["decision"])
print("Boundary Risk Level:", res["risk_assessment"]["risk_level"])
print("Boundary Flags:", res["cautionary_flags"])
assert res["decision"] in ["Hold", "No-Launch"], "Expected Hold or No-Launch for unviable economics!"
print("Boundary Test Passed! [OK]")
