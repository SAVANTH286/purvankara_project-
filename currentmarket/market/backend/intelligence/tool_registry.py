import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.db.connection import get_db
from backend.rag.rag_engine import get_rag_engine
from ml.buyer.infer import evaluate_buyer_fit
from ml.market.infer import predict_market_absorption as run_predict_market_absorption
from ml.price.infer import predict_price_per_sqft as run_predict_price_per_sqft
from backend.services.amenity_service import get_amenity_service
from backend.services.geospatial_service import resolve_coordinates


# -----------------------------------------------------------------------------
# 1. TOOL IMPLEMENTATIONS RETURNING STRUCTURED EVIDENCE
# -----------------------------------------------------------------------------

def get_city_profile() -> Dict[str, Any]:
    """Returns the macro-level residential market profile for Bengaluru."""
    try:
        with get_db() as db:
            row = db.query_one("SELECT * FROM cities WHERE city_name = 'Bengaluru'")
        if not row:
            return {
                "tool": "get_city_profile",
                "status": "unavailable",
                "data": None,
                "source": "Database (cities table)",
                "limitations": ["No city profile record found for Bengaluru."]
            }
        data = dict(row)
        return {
            "tool": "get_city_profile",
            "status": "success",
            "data": data,
            "source": data.get("source", "Knight Frank / Cushman & Wakefield / JLL City Reports"),
            "limitations": ["Macro figures reflect citywide aggregates updated semiannually."]
        }
    except Exception as e:
        return {
            "tool": "get_city_profile",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Database query failed: {str(e)}"]
        }


def list_micro_markets() -> Dict[str, Any]:
    """Returns all 25 canonical micro-markets in Bengaluru with coordinates and baseline signals."""
    try:
        with get_db() as db:
            rows = db.query(
                """
                SELECT micromarket_id, micromarket_name, zone, latitude, longitude,
                       segment_bias, premium_amenability, launch_activity_signal,
                       absorption_signal, average_price_per_sqft, average_percentage_sold,
                       launched_units, absorbed_units, available_units,
                       key_drivers, notes, source
                FROM micro_markets
                ORDER BY zone, micromarket_name
                """
            )
        data = [dict(r) for r in rows]
        return {
            "tool": "list_micro_markets",
            "status": "success",
            "data": {
                "count": len(data),
                "micro_markets": data
            },
            "source": "PostgreSQL / SQLite Micro-Market Registry (25 Canonical Corridors)",
            "limitations": ["Corridor list is restricted to the 25 canonical Bengaluru residential corridors."]
        }
    except Exception as e:
        return {
            "tool": "list_micro_markets",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Database query failed: {str(e)}"]
        }


def get_micro_market_profile(market_name: str) -> Dict[str, Any]:
    """Returns the market metrics and baseline signals for a given micro-market."""
    target = market_name.strip()
    try:
        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target}%",)
            )
        if not row:
            return {
                "tool": "get_micro_market_profile",
                "status": "unavailable",
                "data": None,
                "source": "Micro-Markets Database",
                "limitations": [f"Micro-market '{market_name}' not found among the 25 canonical Bengaluru corridors."]
            }
        data = dict(row)
        return {
            "tool": "get_micro_market_profile",
            "status": "success",
            "data": data,
            "source": data.get("source", "Knight Frank / Cushman & Wakefield / JLL research filings"),
            "limitations": ["Quarterly historical absorption data; micro-topographical variance excluded."]
        }
    except Exception as e:
        return {
            "tool": "get_micro_market_profile",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def get_market_projects(market_name: str) -> Dict[str, Any]:
    """Returns verified real projects in a micro-market."""
    target = market_name.strip()
    try:
        with get_db() as db:
            rows = db.query(
                "SELECT * FROM projects WHERE LOWER(micromarket_name) LIKE LOWER(%s) ORDER BY id ASC",
                (f"%{target}%",)
            )
        data = [dict(r) for r in rows]
        return {
            "tool": "get_market_projects",
            "status": "success",
            "data": {
                "micro_market": market_name,
                "project_count": len(data),
                "projects": data
            },
            "source": "PostgreSQL / SQLite Projects Database (RERA & Sales Records)",
            "limitations": [
                "Projects listed reflect verified developer launches in the registry.",
                "Historical projects are not automatically ongoing competitors unless active inventory remains."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_market_projects",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def get_competitors(market_name: str, segment: Optional[str] = None) -> Dict[str, Any]:
    """Returns competing projects in a micro-market, optionally filtered by segment."""
    target = market_name.strip()
    query = "SELECT * FROM projects WHERE LOWER(micromarket_name) LIKE LOWER(%s)"
    params = [f"%{target}%"]
    if segment:
        query += " AND LOWER(property_segment) = LOWER(%s)"
        params.append(segment.strip())
    query += " ORDER BY price_per_sqft ASC"

    try:
        with get_db() as db:
            rows = db.query(query, tuple(params))
        data = [dict(r) for r in rows]
        return {
            "tool": "get_competitors",
            "status": "success",
            "data": {
                "micro_market": market_name,
                "segment_filter": segment,
                "competitor_count": len(data),
                "competitors": data
            },
            "source": "Verified RERA & Commercial Competitor Registry",
            "limitations": [
                "Competitor registry reflects organized Grade-A developer filings.",
                "Unorganized local plotted developments are excluded.",
                "BHK-specific floor plans are reported where available in filing metadata."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_competitors",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def get_buyer_profiles() -> Dict[str, Any]:
    """Returns aggregated demographic patterns from 2,583 historical customer bookings."""
    try:
        with get_db() as db:
            rows = db.query("SELECT * FROM buyer_profiles ORDER BY id ASC")
        data = [dict(r) for r in rows]
        return {
            "tool": "get_buyer_profiles",
            "status": "success",
            "data": {
                "sample_size": 2583,
                "aggregate_profiles": data
            },
            "source": "2,583 Verified Puravankara Customer Bookings (Atmosphere, Blubelle, Ecopolitan)",
            "limitations": [
                "Aggregated demographic patterns from completed Puravankara assets.",
                "Individual personal identifiable information (PII) is strictly suppressed.",
                "Historical buyer patterns do not guarantee future cohort behaviors."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_buyer_profiles",
            "status": "error",
            "error": str(e),
            "source": "Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def get_buyer_segments(bhk_str: str = "3BHK", property_segment: str = "Mid", price_per_sqft: float = 6500.0, units: Optional[int] = 300) -> Dict[str, Any]:
    """Runs Buyer Intelligence V2 inference matching proposed configuration to empirical demographic segments."""
    model_path = Path("ml/buyer/buyer_segment_model.pkl")
    if not model_path.exists():
        return {
            "tool": "get_buyer_segments",
            "status": "unavailable",
            "reason": "Validated KMeans buyer segmentation model artifact not found at ml/buyer/buyer_segment_model.pkl.",
            "source": "ml/buyer/buyer_segment_model.pkl",
            "limitations": ["No validated Buyer ML model artifact is currently available."]
        }
    try:
        fit = evaluate_buyer_fit(bhk_str, property_segment, price_per_sqft, units)
        return {
            "tool": "get_buyer_segments",
            "status": "success",
            "data": fit,
            "source": "Buyer Intelligence V2 (KMeans k=5, 2,583 verified bookings, Silhouette 0.7209)",
            "limitations": fit.get("limitations", [
                "Buyer Intelligence is strictly location-agnostic: reflects configuration and demographic alignment across 2,583 historical Puravankara booking records, NOT micro-market cleared demand or corridor-specific absorption velocity.",
                "Income disclosure rate was 7.7% in historical records; unrecorded files are preserved without synthetic imputation."
            ])
        }
    except Exception as e:
        return {
            "tool": "get_buyer_segments",
            "status": "error",
            "error": str(e),
            "source": "KMeans Buyer Clustering Model",
            "limitations": [f"Model inference failed: {str(e)}"]
        }


def predict_buyer_fit(bhk_str: str = "3BHK", property_segment: str = "Mid", price_per_sqft: float = 6500.0, units: Optional[int] = 300) -> Dict[str, Any]:
    """Alias for get_buyer_segments providing consistent nomenclature."""
    return get_buyer_segments(bhk_str, property_segment, price_per_sqft, units)


def predict_buyer_segments(bhk_str: str = "3BHK", property_segment: str = "Mid", price_per_sqft: float = 6500.0, units: Optional[int] = 300) -> Dict[str, Any]:
    """Direct alias for get_buyer_segments providing canonical Buyer Intelligence V2 tool access."""
    return get_buyer_segments(bhk_str, property_segment, price_per_sqft, units)


def predict_market_absorption(
    micromarket_name: str,
    units: int = 300,
    price_per_sqft: float = 6500.0,
    unsold_inventory_estimate: Optional[float] = None,
    overhang_months_estimate: Optional[float] = None
) -> Dict[str, Any]:
    """Runs inference on the real Market Demand / Absorption ML model (RandomForestRegressor)."""
    model_path = Path("ml/market/market_demand_model.pkl")
    if not model_path.exists():
        return {
            "tool": "predict_market_absorption",
            "status": "unavailable",
            "reason": "Validated Market Demand ML model artifact not found at ml/market/market_demand_model.pkl.",
            "source": "ml/market/market_demand_model.pkl",
            "limitations": ["No validated Market Demand model artifact is currently available."]
        }
    try:
        pred = run_predict_market_absorption(
            micromarket_name=micromarket_name,
            units=units,
            price_per_sqft=price_per_sqft,
            unsold_inventory_estimate=unsold_inventory_estimate,
            overhang_months_estimate=overhang_months_estimate
        )
        return {
            "tool": "predict_market_absorption",
            "status": "success",
            "data": pred,
            "source": "Random Forest Regressor (100 trees, R²=0.9763, MAE=2.40%)",
            "limitations": [
                "Absorption velocity assumes prevailing macroeconomic interest rate and home-loan stability.",
                "Predictive inference represents baseline market clearing pace, not a guaranteed commercial outcome."
            ]
        }
    except Exception as e:
        return {
            "tool": "predict_market_absorption",
            "status": "error",
            "error": str(e),
            "source": "Market Demand ML Model",
            "limitations": [f"Inference error: {str(e)}"]
        }


def predict_price(
    micromarket_name: str,
    property_segment: str = "Mid",
    property_type: str = "Residential",
    bhk_str: str = "3BHK",
    units: int = 300
) -> Dict[str, Any]:
    """Runs inference on the verified Price Intelligence ML model with empirical coverage gating."""
    try:
        pred = run_predict_price_per_sqft(
            micromarket_name=micromarket_name,
            property_segment=property_segment,
            property_type=property_type,
            bhk_str=bhk_str,
            units=units
        )

        if not pred.get("ml_used") and pred.get("coverage_status") == "UNSUPPORTED":
            return {
                "tool": "predict_price",
                "status": "unsupported",
                "data": pred,
                "source": f"Price Intelligence Registry ({pred.get('model_version', 'v2.0.0-ridge')})",
                "limitations": [pred.get("warning", "Unsupported corridor with 0 verified observations.")]
            }

        limitations = list(pred.get("limitations", []))
        if pred.get("warning"):
            limitations.insert(0, pred["warning"])

        return {
            "tool": "predict_price",
            "status": "success",
            "data": {
                "predicted_price_per_sqft": pred.get("prediction"),
                "coverage_status": pred.get("coverage_status"),
                "confidence_status": pred.get("confidence_status"),
                "market_observation_count": pred.get("market_observation_count"),
                "market_development_count": pred.get("market_development_count"),
                "market_developer_count": pred.get("market_developer_count"),
                "latest_verified_launch_date": pred.get("latest_verified_launch_date"),
                "comparable_projects": pred.get("comparable_projects", []),
                "evidence": pred.get("evidence"),
                "warning": pred.get("warning"),
                "model_version": pred.get("model_version"),
                "feature_coverage": pred.get("feature_coverage")
            },
            "source": f"Price Intelligence Regressor ({pred.get('model_version', 'v2.0.0-ridge')}, {pred.get('algorithm', 'Ridge Regression')})",
            "limitations": limitations
        }
    except Exception as e:
        return {
            "tool": "predict_price",
            "status": "error",
            "error": str(e),
            "source": "Price Intelligence Regressor",
            "limitations": [f"Inference error: {str(e)}"]
        }


def get_infrastructure_amenities(
    market_name: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 5.0
) -> Dict[str, Any]:
    """Returns verified OpenStreetMap amenities within 5 km calculated with Haversine distance."""
    try:
        if (latitude is None or longitude is None) and market_name:
            lat, lon = resolve_coordinates(market_name)
        elif latitude is not None and longitude is not None:
            lat, lon = float(latitude), float(longitude)
        elif market_name:
            lat, lon = resolve_coordinates(market_name)
        else:
            return {
                "tool": "get_infrastructure_amenities",
                "status": "unavailable",
                "data": None,
                "source": "OpenStreetMap Geospatial Service",
                "limitations": ["Missing micro-market name or coordinates to evaluate 5 km radius."]
            }

        res = get_amenity_service().get_amenities_within_radius(lat, lon, radius_km=radius_km)
        return {
            "tool": "get_infrastructure_amenities",
            "status": "success",
            "data": res,
            "source": f"Live OpenStreetMap (OSM) Haversine Radius Query ({radius_km} km centered at {lat:.4f}, {lon:.4f})",
            "limitations": [
                f"Amenities measured via straight-line Haversine distance within a {radius_km} km radius.",
                "Road network traffic travel times may vary based on peak congestion."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_infrastructure_amenities",
            "status": "error",
            "error": str(e),
            "source": "OpenStreetMap",
            "limitations": [f"Geospatial query error: {str(e)}"]
        }


def get_infrastructure_profile(market_name: str) -> Dict[str, Any]:
    """Returns verified transit and road infrastructure notes for a micro-market."""
    target = market_name.strip()
    try:
        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM infrastructure WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target}%",)
            )
        if not row:
            return {
                "tool": "get_infrastructure_profile",
                "status": "unavailable",
                "data": None,
                "source": "Infrastructure Database",
                "limitations": [f"No infrastructure profile record found for '{market_name}'."]
            }
        data = dict(row)
        return {
            "tool": "get_infrastructure_profile",
            "status": "success",
            "data": data,
            "source": "BMRCL Namma Metro & Municipal Infrastructure Registry",
            "limitations": ["Transit operational status reflects current municipal master plan filings."]
        }
    except Exception as e:
        return {
            "tool": "get_infrastructure_profile",
            "status": "error",
            "error": str(e),
            "source": "Infrastructure Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def get_regulatory_records(market_name: str) -> Dict[str, Any]:
    """Returns regulatory clearance baselines and RERA compliance data for a micro-market."""
    target = market_name.strip()
    try:
        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM regulatory_records WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target}%",)
            )
        if not row:
            return {
                "tool": "get_regulatory_records",
                "status": "unavailable",
                "data": None,
                "source": "Karnataka RERA & Municipal Clearance Registry",
                "limitations": [f"No regulatory filings found for '{market_name}'."]
            }
        data = dict(row)
        return {
            "tool": "get_regulatory_records",
            "status": "success",
            "data": data,
            "source": data.get("source", "Karnataka RERA portal verified filings"),
            "limitations": [
                "Approval velocity reflects historical corridor averages (BDA/BBMP).",
                "RERA registration presence does not constitute legal title certification for unverified plots."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_regulatory_records",
            "status": "error",
            "error": str(e),
            "source": "Regulatory Database",
            "limitations": [f"Query error: {str(e)}"]
        }


def search_market_documents(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Performs semantic/keyword retrieval over verified Knight Frank, C&W, JLL, and CBRE research reports."""
    try:
        rag = get_rag_engine()
        results = rag.search(query, top_k=top_k)
        return {
            "tool": "search_market_documents",
            "status": "success",
            "data": {
                "query": query,
                "hit_count": len(results),
                "excerpts": results
            },
            "source": "Institutional Consultant Research Reports (Knight Frank, Cushman & Wakefield, JLL, CBRE)",
            "limitations": [
                "Research findings are extracted from published institutional real estate studies.",
                "Specific macro assertions reflect market conditions as of report publication dates."
            ]
        }
    except Exception as e:
        return {
            "tool": "search_market_documents",
            "status": "error",
            "error": str(e),
            "source": "RAG Document Engine",
            "limitations": [f"Document search error: {str(e)}"]
        }


def get_dss_evidence(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes full multi-agent DSS project evaluation and applies institutional investment committee hurdles.
    Does NOT invent a verdict; uses the exact DecisionEngine output.
    """
    from backend.agents.base import ProjectInput
    from backend.intelligence.orchestrator import get_orchestrator

    try:
        micro_market = project_data.get("micro_market") or project_data.get("location") or "Kanakapura Road"
        proj = ProjectInput(
            project_name=project_data.get("project_name", f"Purva Project ({micro_market})"),
            developer=project_data.get("developer", "Puravankara"),
            property_type=project_data.get("property_type", "Residential"),
            property_segment=project_data.get("property_segment", "Mid"),
            location=micro_market,
            micro_market=micro_market,
            price_per_sqft=float(project_data.get("price_per_sqft", 6500.0)),
            units=int(project_data.get("units", 300)),
            bhk=project_data.get("bhk", "3BHK"),
            launch_date=project_data.get("launch_date", "2026-10-01")
        )
        orchestrator = get_orchestrator()
        eval_res = orchestrator.evaluate_project(proj)
        return {
            "tool": "get_dss_evidence",
            "status": "success",
            "data": {
                "decision": eval_res.get("decision"),
                "executive_summary": eval_res.get("executive_summary"),
                "composite_risk_score": eval_res.get("risk_score"),
                "risk_tier": eval_res.get("risk_assessment", {}).get("risk_category"),
                "risk_breakdown": eval_res.get("risk_assessment", {}).get("risk_breakdown"),
                "financial_metrics": eval_res.get("financial_metrics"),
                "hurdle_rules": "Launch: Abs>=80% & Margin>=18% & Risk<55; Hold: Abs>=65% & Margin>=14% & Risk<70; Else: No-Launch"
            },
            "source": "Puravankara Institutional DSS Engine (Multi-Agent Audit & Decision Hurdle Rules)",
            "limitations": [
                "Decision verdict reflects automated Investment Committee hurdle criteria based on evaluated project parameters.",
                "Actual capital commitment requires formal board ratification."
            ]
        }
    except Exception as e:
        return {
            "tool": "get_dss_evidence",
            "status": "error",
            "error": str(e),
            "source": "DSS Orchestrator",
            "limitations": [f"DSS evaluation error: {str(e)}"]
        }


def run_scenario(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes What-If sensitivity analysis (price, scale, BHK) via the Scenario Engine.
    Returns quantitative deltas, empirical absorption shifts, risk changes, and synchronized verdict.
    """
    from backend.agents.base import ProjectInput
    from backend.engine.scenario_engine import ScenarioRequest, get_scenario_engine

    try:
        micro_market = scenario_data.get("micro_market") or "Kanakapura Road"
        base_proj = ProjectInput(
            project_name=scenario_data.get("project_name", f"Purva Project ({micro_market})"),
            developer="Puravankara",
            property_type="Residential",
            property_segment="Mid",
            location=micro_market,
            micro_market=micro_market,
            price_per_sqft=float(scenario_data.get("base_price_per_sqft", 6500.0)),
            units=int(scenario_data.get("base_units", 300)),
            bhk=scenario_data.get("base_bhk", "3BHK")
        )

        req = ScenarioRequest(
            base_project=base_proj,
            scenario_name=scenario_data.get("scenario_name", "What-If Analysis"),
            new_price_per_sqft=float(scenario_data["new_price_per_sqft"]) if "new_price_per_sqft" in scenario_data else None,
            new_units=int(scenario_data["new_units"]) if "new_units" in scenario_data else None,
            new_bhk=scenario_data.get("new_bhk"),
            launch_delay_months=int(scenario_data.get("launch_delay_months", 0)),
            competitor_launch_month=max(1, int(scenario_data.get("competitor_launch_month") or 4)),
            competitor_project_id=scenario_data.get("competitor_project_id"),
            competitor_price_per_sqft=float(scenario_data["competitor_price_per_sqft"]) if "competitor_price_per_sqft" in scenario_data else None,
            intervention_month=max(1, int(scenario_data.get("intervention_month") or 6)),
            intervention_price_adjustment_pct=float(scenario_data.get("intervention_price_adjustment_pct", -5.0)),
            simulation_months=int(scenario_data.get("simulation_months", 12)),
            simulation_seed=int(scenario_data.get("simulation_seed", 42))
        )

        engine = get_scenario_engine()
        scen_res = engine.run_scenario(req)
        return {
            "tool": "run_scenario",
            "status": "success",
            "data": {
                "decision": scen_res.get("decision"),
                "decision_result_id": scen_res.get("decision_result_id"),
                "baseline": scen_res.get("baseline"),
                "blind_spot": scen_res.get("blind_spot"),
                "competition": scen_res.get("competition"),
                "intervention": scen_res.get("intervention"),
                "blind_spot_loss_cr": scen_res.get("blind_spot_loss_cr"),
                "intervention_recovery_cr": scen_res.get("intervention_recovery_cr"),
                "recovery_percentage": scen_res.get("recovery_percentage"),
                "monthly_trajectory": scen_res.get("monthly_trajectory"),
                "scenario_evidence": scen_res.get("scenario_evidence"),
                "base": scen_res.get("base"),
                "scenario": scen_res.get("scenario"),
                "deltas": scen_res.get("delta"),
                "scenario_verdict": scen_res.get("decision"),
                "how_calculated": scen_res.get("how_calculated")
            },
            "source": "Scenario Engine (Baseline, Blind Spot, Competition, Intervention Trajectories & DecisionEngine Verdict)",
            "limitations": [
                "Competitor launch timing and 25% sales pace deceleration are scenario assumptions, not empirical laws.",
                "The official verdict is rendered strictly by DecisionEngine based on institutional hurdles."
            ]
        }
    except Exception as e:
        return {
            "tool": "run_scenario",
            "status": "error",
            "error": str(e),
            "source": "Scenario Engine",
            "limitations": [f"Scenario execution error: {str(e)}"]
        }


# -----------------------------------------------------------------------------
# 2. SAFE EXECUTION DISPATCHER & SECURITY VALIDATOR
# -----------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "get_city_profile": lambda args: get_city_profile(),
    "list_micro_markets": lambda args: list_micro_markets(),
    "get_micro_market_profile": lambda args: get_micro_market_profile(args.get("market_name", "Kanakapura Road")),
    "get_market_projects": lambda args: get_market_projects(args.get("market_name", "Kanakapura Road")),
    "get_competitors": lambda args: get_competitors(args.get("market_name", "Kanakapura Road"), args.get("segment")),
    "get_buyer_profiles": lambda args: get_buyer_profiles(),
    "get_buyer_segments": lambda args: get_buyer_segments(
        args.get("bhk_str", "3BHK"),
        args.get("property_segment", "Mid"),
        float(args.get("price_per_sqft", 6500.0)),
        int(args.get("units", 300))
    ),
    "predict_buyer_fit": lambda args: predict_buyer_fit(
        args.get("bhk_str", "3BHK"),
        args.get("property_segment", "Mid"),
        float(args.get("price_per_sqft", 6500.0)),
        int(args.get("units", 300))
    ),
    "predict_buyer_segments": lambda args: predict_buyer_segments(
        args.get("bhk_str", "3BHK"),
        args.get("property_segment", "Mid"),
        float(args.get("price_per_sqft", 6500.0)),
        int(args.get("units", 300))
    ),
    "predict_market_absorption": lambda args: predict_market_absorption(
        micromarket_name=args.get("micromarket_name", "Kanakapura Road"),
        units=int(args.get("units", 300)),
        price_per_sqft=float(args.get("price_per_sqft", 6500.0))
    ),
    "predict_price": lambda args: predict_price(
        micromarket_name=args.get("micromarket_name", "Kanakapura Road"),
        property_segment=args.get("property_segment", "Mid"),
        property_type=args.get("property_type", "Residential"),
        bhk_str=args.get("bhk_str", "3BHK"),
        units=int(args.get("units", 300))
    ),
    "get_infrastructure_amenities": lambda args: get_infrastructure_amenities(
        market_name=args.get("market_name"),
        latitude=args.get("latitude"),
        longitude=args.get("longitude"),
        radius_km=float(args.get("radius_km", 5.0))
    ),
    "get_infrastructure_profile": lambda args: get_infrastructure_profile(args.get("market_name", "Kanakapura Road")),
    "get_regulatory_records": lambda args: get_regulatory_records(args.get("market_name", "Kanakapura Road")),
    "search_market_documents": lambda args: search_market_documents(args.get("query", "")),
    "get_dss_evidence": lambda args: get_dss_evidence(args),
    "run_scenario": lambda args: run_scenario(args)
}


def execute_tool(func_name: str, arguments: dict) -> Dict[str, Any]:
    """
    Safely executes an approved tool from the registry with strict allow-list security.
    Blocks arbitrary code execution, SQL generation, filesystem access, and arbitrary URLs.
    """
    if func_name not in TOOL_FUNCTIONS:
        return {
            "tool": func_name,
            "status": "error",
            "error": f"Tool '{func_name}' is not registered in the approved intelligence tool catalog.",
            "source": "Security Validator",
            "limitations": ["Execution blocked: tool name not in approved catalog."]
        }

    try:
        return TOOL_FUNCTIONS[func_name](arguments or {})
    except Exception as e:
        return {
            "tool": func_name,
            "status": "error",
            "error": str(e),
            "source": "Tool Execution Engine",
            "limitations": [f"Execution error while running '{func_name}': {str(e)}"]
        }


# -----------------------------------------------------------------------------
# 3. EXPORTED TOOL CATALOG WITH STRICT PARAMETER SCHEMAS
# -----------------------------------------------------------------------------

TOOL_CATALOG: List[Dict[str, Any]] = [
    {
        "name": "get_city_profile",
        "description": "Returns macro residential market overview for Bengaluru (launches, unsold inventory, QTS, price growth).",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "list_micro_markets",
        "description": "Returns list of all 25 canonical micro-markets in Bengaluru with zone, coordinates, and baseline signals.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_micro_market_profile",
        "description": "Returns supply, absorption %, price/sqft, and drivers for a specific micro-market (e.g., 'Kanakapura Road', 'Bagalur', 'Whitefield').",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "The micro-market name in Bengaluru"}
            },
            "required": ["market_name"]
        }
    },
    {
        "name": "get_market_projects",
        "description": "Returns verified projects in a micro-market with developer, price, and absorption status.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "The micro-market name"}
            },
            "required": ["market_name"]
        }
    },
    {
        "name": "get_competitors",
        "description": "Returns competing developer projects in a micro-market, optionally filtered by segment.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "The micro-market name"},
                "segment": {"type": "string", "description": "Property segment (e.g., 'Mid', 'Premium')"}
            },
            "required": ["market_name"]
        }
    },
    {
        "name": "get_buyer_profiles",
        "description": "Returns aggregated demographic profiles from 2,583 verified customer bookings across Atmosphere, Blubelle, and Ecopolitan.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_buyer_segments",
        "description": "Predicts buyer demographic cluster and fit using real KMeans model trained on 2,583 buyer records.",
        "parameters": {
            "type": "object",
            "properties": {
                "bhk_str": {"type": "string", "description": "Target configuration, e.g., '2BHK', '3BHK', '4BHK'"},
                "property_segment": {"type": "string", "description": "Segment, e.g., 'Mid', 'Premium'"},
                "price_per_sqft": {"type": "number", "description": "Proposed price per sqft in INR"},
                "units": {"type": "integer", "description": "Proposed project units count"}
            }
        }
    },
    {
        "name": "predict_buyer_segments",
        "description": "Evaluates project configuration alignment against empirical historical buyer segments and demographic cohorts (KMeans k=5, 2,583 records, Silhouette 0.7209).",
        "parameters": {
            "type": "object",
            "properties": {
                "bhk_str": {"type": "string", "description": "Target configuration, e.g., '2BHK', '3BHK', '4BHK'"},
                "property_segment": {"type": "string", "description": "Segment, e.g., 'Mid', 'Premium'"},
                "price_per_sqft": {"type": "number", "description": "Proposed price per sqft in INR"},
                "units": {"type": "integer", "description": "Proposed project units count"}
            }
        }
    },
    {
        "name": "predict_market_absorption",
        "description": "Predicts project absorption % and volume using real Random Forest Regressor ML model.",
        "parameters": {
            "type": "object",
            "properties": {
                "micromarket_name": {"type": "string", "description": "The micro-market name"},
                "units": {"type": "integer", "description": "Proposed unit count"},
                "price_per_sqft": {"type": "number", "description": "Proposed price per sqft in INR"}
            },
            "required": ["micromarket_name"]
        }
    },
    {
        "name": "predict_price",
        "description": "Predicts market-clearing realization in INR/sq.ft using real Gradient Boosting Regressor ML model.",
        "parameters": {
            "type": "object",
            "properties": {
                "micromarket_name": {"type": "string", "description": "The micro-market name"},
                "property_segment": {"type": "string", "description": "Segment (e.g., 'Mid', 'High-end / Luxury')"},
                "bhk_str": {"type": "string", "description": "Configuration (e.g., '2BHK', '3BHK')"},
                "units": {"type": "integer", "description": "Proposed unit count"}
            },
            "required": ["micromarket_name"]
        }
    },
    {
        "name": "get_infrastructure_amenities",
        "description": "Retrieves real verified amenities within 5 km of coordinates or micro-market from OpenStreetMap.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "Micro-market name or corridor"},
                "radius_km": {"type": "number", "description": "Search radius in km (default 5.0)"}
            }
        }
    },
    {
        "name": "get_infrastructure_profile",
        "description": "Returns transit and road infrastructure notes (Metro lines, highways) for a micro-market.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "The micro-market name"}
            },
            "required": ["market_name"]
        }
    },
    {
        "name": "get_regulatory_records",
        "description": "Returns RERA compliance rate, approval timelines, and litigation status for a micro-market.",
        "parameters": {
            "type": "object",
            "properties": {
                "market_name": {"type": "string", "description": "The micro-market name"}
            },
            "required": ["market_name"]
        }
    },
    {
        "name": "search_market_documents",
        "description": "Searches verified consultant reports (Knight Frank, Cushman & Wakefield, JLL, CBRE) for real estate analysis.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query keywords"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_dss_evidence",
        "description": "Executes full multi-agent project evaluation, composite risk calculation, and Investment Committee hurdle determination (Launch/Hold/No-Launch).",
        "parameters": {
            "type": "object",
            "properties": {
                "micro_market": {"type": "string", "description": "Target corridor"},
                "units": {"type": "integer", "description": "Planned unit count"},
                "price_per_sqft": {"type": "number", "description": "Proposed price in INR/sq.ft"},
                "bhk": {"type": "string", "description": "Unit configuration (e.g. '3BHK')"},
                "property_segment": {"type": "string", "description": "Segment (e.g. 'Mid', 'Premium')"}
            }
        }
    },
    {
        "name": "run_scenario",
        "description": "Executes 12-month What-If simulation across Baseline, Blind Spot, Competition, and Intervention dimensions, returning revenue loss, recovery %, trajectory, and official DecisionEngine verdict.",
        "parameters": {
            "type": "object",
            "properties": {
                "micro_market": {"type": "string", "description": "Target corridor"},
                "base_price_per_sqft": {"type": "number", "description": "Baseline price"},
                "base_units": {"type": "integer", "description": "Baseline units"},
                "base_bhk": {"type": "string", "description": "Baseline BHK"},
                "new_price_per_sqft": {"type": "number", "description": "Scenario price"},
                "new_units": {"type": "integer", "description": "Scenario units"},
                "new_bhk": {"type": "string", "description": "Scenario BHK"},
                "competitor_launch_month": {"type": "integer", "description": "Month competitor launches (default 4)"},
                "competitor_project_id": {"type": "integer", "description": "Optional real competitor project ID"},
                "competitor_price_per_sqft": {"type": "number", "description": "Competitor price/sqft"},
                "intervention_month": {"type": "integer", "description": "Month management intervenes (default 6)"},
                "intervention_price_adjustment_pct": {"type": "number", "description": "Price adjustment % at intervention (default -5.0)"},
                "simulation_months": {"type": "integer", "description": "Simulation horizon (default 12)"},
                "simulation_seed": {"type": "integer", "description": "Random seed (default 42)"}
            }
        }
    }
]

AVAILABLE_TOOLS = TOOL_CATALOG

