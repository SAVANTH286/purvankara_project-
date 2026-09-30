from typing import Dict, Any, List

AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "city_profile_agent": {
        "name": "city_profile_agent",
        "display_name": "City Macro Intelligence Agent",
        "description": "Evaluates macro-level residential market trends, annual launch volumes, citywide unsold stock, quarters-to-sell (QTS), and zonal distribution across Bengaluru.",
        "capabilities": [
            "Macro supply-demand equilibrium",
            "Annual launch volume tracking",
            "Quarters-to-sell (QTS) inventory health",
            "Zonal launch share distribution"
        ],
        "allowed_tools": ["get_city_profile", "list_micro_markets"],
        "parameter_requirements": [],
        "evidence_format": "Macro indicators, historical annual counts, QTS ratio, consultant source citation."
    },
    "location_agent": {
        "name": "location_agent",
        "display_name": "Location & Connectivity Agent",
        "description": "Evaluates micro-market corridor accessibility, arterial road networks, tech park proximity, and highway connectivity.",
        "capabilities": [
            "Corridor road network analysis",
            "Tech park and employment node connectivity",
            "Micro-market coordinate resolution",
            "Corridor geographic categorization"
        ],
        "allowed_tools": ["get_micro_market_profile", "list_micro_markets"],
        "parameter_requirements": ["market_name"],
        "evidence_format": "Corridor coordinates, zone, primary transit drivers, regional notes."
    },
    "market_agent": {
        "name": "market_agent",
        "display_name": "Market Demand & Absorption Agent",
        "description": "Analyzes micro-market supply conditions, launched vs absorbed unit volumes, historical absorption velocity, quarterly overhang, and project scale demand.",
        "capabilities": [
            "Micro-market historical absorption rates",
            "Inventory overhang months calculation",
            "Corridor project distribution and pricing benchmarks",
            "Market demand absorption ML inference"
        ],
        "allowed_tools": [
            "get_micro_market_profile",
            "list_micro_markets",
            "get_market_projects",
            "predict_market_absorption"
        ],
        "parameter_requirements": ["market_name"],
        "evidence_format": "Launched units, absorbed units, absorption %, overhang months, ML predicted absorption velocity."
    },
    "competition_agent": {
        "name": "competition_agent",
        "display_name": "Competition & Supply Intelligence Agent",
        "description": "Evaluates competing residential projects, Grade-A developer presence (Prestige, Sobha, Brigade, Godrej), pricing bands, and absorption status.",
        "capabilities": [
            "RERA-filed competitor project discovery",
            "Developer tier and pricing band comparison",
            "Corridor competitor density and supply clustering"
        ],
        "allowed_tools": ["get_competitors", "get_market_projects"],
        "parameter_requirements": ["market_name"],
        "evidence_format": "List of comparable projects, developer names, pricing/sq.ft, % sold, property segments."
    },
    "infrastructure_agent": {
        "name": "infrastructure_agent",
        "display_name": "Geospatial & Infrastructure Agent",
        "description": "Audits live geospatial amenities within a 5 km radius using OpenStreetMap telemetry, operational Namma Metro lines, arterial highways, and civic utilities.",
        "capabilities": [
            "5 km radius OpenStreetMap POI spatial query",
            "Exact Haversine distance calculations to nearest transit, schools, hospitals",
            "Metro corridor connectivity and civic utility status"
        ],
        "allowed_tools": ["get_infrastructure_amenities", "get_infrastructure_profile"],
        "parameter_requirements": ["market_name"],
        "evidence_format": "Count of POIs by category, nearest verified landmarks with exact km distances, metro operational notes."
    },
    "buyer_intelligence_agent": {
        "name": "buyer_intelligence_agent",
        "display_name": "Buyer Persona & Demographics Agent",
        "description": "Analyzes verified buyer demographics from 2,583 historical booking records, household income hurdles, first-home buyer share, and KMeans buyer fit.",
        "capabilities": [
            "Historical buyer demographic pattern analysis",
            "Household income band matching",
            "First-home buyer propensity tracking",
            "KMeans demographic clustering and Buyer Fit Index inference"
        ],
        "allowed_tools": [
            "predict_buyer_segments",
            "get_buyer_segments",
            "get_buyer_profiles",
            "predict_buyer_fit"
        ],
        "parameter_requirements": [],
        "evidence_format": "Dominant persona, average income, first-home %, target configuration fit index (0.50-1.00)."
    },
    "finance_agent": {
        "name": "finance_agent",
        "display_name": "Financial Feasibility & Realization Agent",
        "description": "Models development economics, saleable area geometry, top-line gross realization revenue, cost structures, and gross margins.",
        "capabilities": [
            "Built-up and saleable area calculations",
            "Gross realization revenue modeling",
            "Gross margin and break-even percentage computation",
            "ML market clearing price benchmark prediction"
        ],
        "allowed_tools": ["predict_price", "run_scenario"],
        "parameter_requirements": ["market_name"],
        "evidence_format": "Saleable area, projected revenue, gross margin %, optimal clearing price benchmark."
    },
    "regulatory_agent": {
        "name": "regulatory_agent",
        "display_name": "Regulatory & RERA Compliance Agent",
        "description": "Assesses Karnataka RERA registration compliance rates, municipal approval cycles (BDA/BBMP), and litigation risk density.",
        "capabilities": [
            "RERA compliance rate auditing",
            "Average municipal sanction timeline tracking",
            "Master Plan conforming use and litigation density"
        ],
        "allowed_tools": ["get_regulatory_records"],
        "parameter_requirements": ["market_name"],
        "evidence_format": "RERA compliance %, average approval timeline in months, litigation risk rating, zoning notes."
    },
    "project_execution_agent": {
        "name": "project_execution_agent",
        "display_name": "Project Execution & Governance Agent",
        "description": "Evaluates developer delivery track record, contractor packaging, and construction milestone velocity.",
        "capabilities": [
            "Construction timeline velocity assessment",
            "Contractor qualification and execution risk evaluation"
        ],
        "allowed_tools": ["get_dss_evidence"],
        "parameter_requirements": [],
        "evidence_format": "Execution score, delivery pedigree ratings, construction risk factor."
    },
    "portfolio_agent": {
        "name": "portfolio_agent",
        "display_name": "Portfolio Strategy & Capital Allocation Agent",
        "description": "Evaluates portfolio diversification across Bengaluru zones and ensures project parameters align with corporate investment hurdle thresholds.",
        "capabilities": [
            "Zonal capital allocation alignment",
            "Investment hurdle rate compliance"
        ],
        "allowed_tools": ["get_dss_evidence", "list_micro_markets"],
        "parameter_requirements": [],
        "evidence_format": "Portfolio fit rating, zonal allocation check, investment committee hurdle alignment."
    },
    # System-Level Capabilities
    "dss_evidence_tool": {
        "name": "dss_evidence_tool",
        "display_name": "DSS Evaluation & Hurdle Engine",
        "description": "Executes full multi-attribute project evaluation across all 10 domain agents, calculates composite risk, and applies investment committee hurdles (Launch/Hold/No-Launch).",
        "capabilities": [
            "Full project evaluation execution",
            "Composite risk scoring (0-100)",
            "Deterministic hurdle rate verdict determination"
        ],
        "allowed_tools": ["get_dss_evidence"],
        "parameter_requirements": ["micro_market"],
        "evidence_format": "Decision verdict (Launch/Hold/No-Launch), composite risk score, risk factor breakdown, executive summary."
    },
    "scenario_tool": {
        "name": "scenario_tool",
        "display_name": "What-If Scenario Sensitivity Engine",
        "description": "Simulates changes to Price per sq.ft, Planned Scale, and BHK to observe commercial deltas, data-driven absorption shifts, and synchronized verdict updates.",
        "capabilities": [
            "Financial realization geometry deltas",
            "Empirical price elasticity and RF scale sensitivity",
            "Dynamic risk recalibration and verdict synchronization"
        ],
        "allowed_tools": ["run_scenario"],
        "parameter_requirements": ["micro_market"],
        "evidence_format": "Baseline vs scenario comparison, deltas for revenue/margin/absorption/risk, synchronized scenario verdict."
    },
    "document_search_tool": {
        "name": "document_search_tool",
        "display_name": "Research Document RAG Search",
        "description": "Searches verified institutional consultant research reports (Knight Frank, Cushman & Wakefield, JLL, CBRE) for Bangalore real estate market intelligence.",
        "capabilities": [
            "Semantic/keyword document retrieval",
            "Consultant research citation and excerpt extraction"
        ],
        "allowed_tools": ["search_market_documents"],
        "parameter_requirements": ["query"],
        "evidence_format": "Excerpts from verified consultant reports with document name and section headers."
    }
}


def list_registered_agents() -> List[Dict[str, Any]]:
    """Returns a list of all registered agents with their metadata."""
    return list(AGENT_REGISTRY.values())


def get_agent_info(agent_name: str) -> Dict[str, Any]:
    """Returns metadata for a specific agent name."""
    return AGENT_REGISTRY.get(agent_name, {})
