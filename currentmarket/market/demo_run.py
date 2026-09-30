import json
from backend.agents.base import ProjectInput
from backend.dss_api import evaluate_project


def print_divider(title=""):
    if title:
        print(f"\n{'='*20} {title.upper()} {'='*20}")
    else:
        print("=" * 60)


def run_evaluation(project: ProjectInput):
    print_divider(f"EVALUATING: {project.project_name}")
    print(f"Developer    : {project.developer}")
    print(f"Micro-Market : {project.micro_market} ({project.property_segment})")
    print(f"Config       : {project.bhk} | {project.units} Units | Rs.{project.price_per_sqft:,.0f}/sq.ft")
    print(f"Buyer Intel  : {'Enabled' if project.include_buyer_intelligence else 'Disabled'}")

    res = evaluate_project(project)

    # 1. Decision Banner
    dec = res["decision"].upper()
    print("\n" + "#" * 60)
    conf = res.get('confidence_percentage') or res.get('confidence') or res.get('evidence_coverage') or 'N/A'
    print(f"  >>> VERDICT: [{dec}] (Confidence / Evidence Coverage: {conf}%) <<<")
    print("#" * 60)
    print(f"Summary: {res['executive_summary']}")

    # 2. Risk Profile
    risk = res["risk_assessment"]
    print(f"\n[RISK PROFILE] Level: {risk['risk_level']} (Score: {risk['composite_risk_score']}/100)")
    for r_k, r_v in risk["breakdown"].items():
        print(f"  - {r_k.replace('_', ' ').title():<22}: {r_v}/100")

    # 3. Explainable Why (Drivers, Flags, Actions)
    print("\n[EXPLAINABLE 'WHY' RATIONALE]")
    print("  Positive Drivers (+):")
    for d in res["positive_drivers"]:
        print(f"    * {d}")
    print("  Cautionary Flags (!):")
    for f in res["cautionary_flags"]:
        print(f"    * {f}")
    print("  Recommended Actions (->):")
    for a in res["recommended_actions"]:
        print(f"    * {a}")

    # 4. Clean Observations (Step 1 requirement)
    print("\n[CLEAN CONSOLIDATED OBSERVATIONS]")
    for idx, obs in enumerate(res["observations"], 1):
        print(f"  {idx}. {obs}")

    # 5. 8-Agent Scorecard
    print("\n[8 SPECIALIZED AGENTS SCORECARD]")
    for agent_key, data in res["evidence"].items():
        status_symbol = "[+]" if data["status"] == "supportive" else ("[!]" if data["status"] == "caution" else "[-]")
        print(f"  {status_symbol} {data['agent_name']:<32}: Score {data['score']}/10 ({data['status'].upper()})")
        # Print one highlight metric
        km = data.get("key_metrics", {})
        if agent_key == "market":
            print(f"      -> Absorption: {km.get('absorption_rate_percentage', 'N/A')}% | Overhang: {km.get('overhang_months', 'N/A')} Mos")
        elif agent_key == "competition":
            print(f"      -> Comparables: {km.get('comparable_project_count', 'N/A')} | BHK Coverage: {km.get('coverage_status') or km.get('bhk_coverage_status') or 'N/A'}")
        elif agent_key == "finance":
            print(f"      -> Gross Margin: {km.get('gross_margin_pct', 'N/A')}% | Break-Even: {km.get('break_even_units', 'N/A')} units")
        elif agent_key == "infrastructure":
            print(f"      -> Metro: {km.get('metro_line', 'N/A')} | Flood Risk: Level {km.get('flood_risk_score', 'N/A')}/5")


def main():
    # Case 1: The Canonical Kanakapura Road test from the ChatGPT chat
    p1 = ProjectInput(
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
    run_evaluation(p1)

    # Case 2: Bagalur North Corridor Pilot
    p2 = ProjectInput(
        project_name="Purva AeroCity",
        developer="Puravankara",
        property_type="Residential",
        property_segment="Mid",
        location="Bagalur",
        micro_market="Bagalur",
        price_per_sqft=7200.0,
        units=450,
        bhk="2BHK",
        launch_date="2026-11-15",
        include_buyer_intelligence=True
    )
    run_evaluation(p2)

    # Case 3: Boundary Case - Unviable Pricing (Sub-cost realization)
    p3 = ProjectInput(
        project_name="High Risk Margin Test",
        developer="Puravankara",
        property_type="Residential",
        property_segment="Mid",
        location="Peripheral Far South",
        micro_market="Attibele-Chandapur",
        price_per_sqft=3500.0,
        units=400,
        bhk="3BHK",
        launch_date="2026-10-01",
        include_buyer_intelligence=False
    )
    run_evaluation(p3)


if __name__ == "__main__":
    main()
