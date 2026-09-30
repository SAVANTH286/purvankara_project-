import json
from backend.agents.base import ProjectInput
from backend.dss_api import evaluate_project

test_payload = ProjectInput(
    project_name="Test Proposed Project",
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

res = evaluate_project(test_payload)
print("=== DECISION ===")
print("Decision:", res["decision"])
print("Confidence:", res["confidence_percentage"], "%")
print("Executive Summary:", res["executive_summary"])

print("\n=== EXPLAINABLE WHY RATIONALE ===")
print("Drivers:", res["positive_drivers"])
print("Flags:", res["cautionary_flags"])
print("Actions:", res["recommended_actions"])

print("\n=== OBSERVATIONS ===")
for obs in res["observations"]:
    print(" -", obs)

print("\n=== 8 EVIDENCE AGENTS ===")
for agent_key in res["evidence"]:
    print(f" - [{agent_key.upper()}]: status={res['evidence'][agent_key]['status']}, score={res['evidence'][agent_key]['score']}")
