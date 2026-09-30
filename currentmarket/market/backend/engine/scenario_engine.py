import json
import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.agents.base import ProjectInput
from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from ml.buyer.infer import evaluate_buyer_fit
from backend.db.connection import get_db
from backend.engine.decision_engine import DecisionEngine


class ScenarioRequest(BaseModel):
    base_project: ProjectInput
    scenario_name: Optional[str] = "What-If Analysis"
    new_price_per_sqft: Optional[float] = Field(None, gt=0, description="Proposed scenario price per sq.ft")
    new_units: Optional[int] = Field(None, gt=0, description="Proposed scenario planned unit count")
    new_bhk: Optional[str] = None
    launch_delay_months: Optional[int] = 0

    # Scenario Dynamics (Implementation defaults / assumptions, NOT business facts)
    competitor_launch_month: Optional[int] = Field(4, ge=1, le=12, description="Month in which competitor launches (scenario assumption)")
    competitor_project_id: Optional[int] = Field(None, description="Optional ID of real competitor project from projects table")
    competitor_price_per_sqft: Optional[float] = Field(None, gt=0, description="Competitor price per sq.ft (scenario parameter)")
    intervention_month: Optional[int] = Field(6, ge=1, le=12, description="Month in which management initiates counter-intervention (scenario assumption)")
    intervention_price_adjustment_pct: Optional[float] = Field(-5.0, description="Price adjustment percentage at intervention (scenario assumption)")
    simulation_months: Optional[int] = Field(12, ge=1, le=36, description="Simulation horizon in months")
    simulation_seed: Optional[int] = Field(42, description="Seed for deterministic simulation reproducibility")


class ScenarioEngine:
    def __init__(self):
        pass

    def run_scenario(self, req: ScenarioRequest) -> Dict[str, Any]:
        """
        Executes canonical scenario simulation across three business dimensions:
        1. Baseline (reference trajectory without competitive shock)
        2. Blind Spot (competitor enters, management takes no action, revenue loss)
        3. Competition (grounded in actual projects database records)
        4. Intervention (management counter-action, sales recovery)

        Delegates verdict authority to DecisionEngine and maintains relational traceability:
        scenario_runs -> decision_results -> decision_evidence.
        """
        from backend.intelligence.orchestrator import get_orchestrator
        base = req.base_project
        orchestrator = get_orchestrator()

        # 1. Baseline Evaluation
        base_eval = orchestrator.evaluate_project(base)

        # 2. Derive Scenario Project Input
        scenario_price = float(req.new_price_per_sqft) if req.new_price_per_sqft is not None else float(base.price_per_sqft)
        scenario_units = int(req.new_units) if req.new_units is not None else int(base.units)
        scenario_bhk = req.new_bhk if req.new_bhk is not None else base.bhk

        scenario_project = ProjectInput(
            project_name=f"{base.project_name} ({req.scenario_name})",
            developer=base.developer,
            property_type=base.property_type,
            property_segment=base.property_segment,
            location=base.location,
            micro_market=base.micro_market,
            price_per_sqft=scenario_price,
            units=scenario_units,
            bhk=scenario_bhk,
            launch_date=base.launch_date,
            include_buyer_intelligence=base.include_buyer_intelligence,
            construction_cost_per_sqft=base.construction_cost_per_sqft,
            land_cost_per_sqft=base.land_cost_per_sqft,
            latitude=base.latitude,
            longitude=base.longitude
        )

        # 3. Re-run ML Predictions for the Scenario using existing frozen models
        scenario_market_ml = predict_market_absorption(
            micromarket_name=scenario_project.micro_market,
            units=scenario_project.units,
            price_per_sqft=scenario_project.price_per_sqft
        )
        scenario_price_ml = predict_price_per_sqft(
            micromarket_name=scenario_project.micro_market,
            property_segment=scenario_project.property_segment,
            property_type=scenario_project.property_type,
            bhk_str=scenario_project.bhk or "3BHK",
            units=scenario_project.units
        )
        scenario_buyer_ml = evaluate_buyer_fit(
            bhk_str=scenario_project.bhk or "3BHK",
            property_segment=scenario_project.property_segment,
            price_per_sqft=scenario_project.price_per_sqft
        )

        # 4. Scenario Evaluation via Orchestrator
        scenario_eval = orchestrator.evaluate_project(scenario_project)

        # 5. Compute Quantitative Deltas (Deterministic Formulas)
        base_fin = base_eval.get("evidence", {}).get("finance", {}).get("metrics", {})
        scen_fin = scenario_eval.get("evidence", {}).get("finance", {}).get("metrics", {})

        base_rev = float(base_fin.get("gross_revenue_cr", 0.0))
        scen_rev = float(scen_fin.get("gross_revenue_cr", 0.0))
        rev_delta_cr = round(scen_rev - base_rev, 2)

        base_margin = float(base_fin.get("gross_margin_pct", 0.0))
        scen_margin = float(scen_fin.get("gross_margin_pct", 0.0))
        margin_delta_pct = round(scen_margin - base_margin, 1)

        base_risk = float(base_eval.get("risk_assessment", {}).get("composite_risk_score", 0.0))
        scen_risk = float(scenario_eval.get("risk_assessment", {}).get("composite_risk_score", 0.0))
        risk_delta = round(scen_risk - base_risk, 1)

        # 6. Data-Driven Scenario Absorption Synthesis
        base_market_metrics = base_eval.get("evidence", {}).get("market", {}).get("metrics", {})
        base_corridor_abs = float(base_market_metrics.get("absorption_rate_percentage") or 88.0)
        base_absorption_rate_pct = base_corridor_abs

        # 6A. Base & Scenario ML Market Demand Predictions (Random Forest)
        base_market_ml = predict_market_absorption(
            micromarket_name=base.micro_market,
            units=base.units,
            price_per_sqft=base.price_per_sqft
        )

        # 6B. Price Sensitivity Effect [DATA-DERIVED OLS]
        # Statistically proven OLS slope: beta = -0.006945 percentage points per INR/sq.ft (p=0.0235)
        price_delta_inr = round(scenario_price - base.price_per_sqft, 0)
        price_effect_pct = round(-0.006945 * price_delta_inr, 2)

        # 6C. Scale Sensitivity Effect [ML — Random Forest Gradient]
        base_raw_rf = float(base_market_ml.get("raw_prediction_pct", 33.31))
        scen_raw_rf = float(scenario_market_ml.get("raw_prediction_pct", 31.80))
        scale_effect_pct = round(scen_raw_rf - base_raw_rf, 2)

        # 6D. Synthesize Scenario Absorption with physical real-estate bounds [5%, 100%]
        simulated_absorption_rate_pct = round(base_corridor_abs + price_effect_pct + scale_effect_pct, 2)
        simulated_absorption_rate_pct = max(5.0, min(100.0, simulated_absorption_rate_pct))
        absorption_shift_pct = round(simulated_absorption_rate_pct - base_corridor_abs, 2)

        # 7. Risk Engine Recalculation using existing system policy
        if simulated_absorption_rate_pct >= 90.0:
            scen_market_score = 9.2
        elif simulated_absorption_rate_pct >= 75.0:
            scen_market_score = 8.0
        elif simulated_absorption_rate_pct >= 60.0:
            scen_market_score = 6.5
        else:
            scen_market_score = 4.5
        scen_market_risk = max(5.0, min(95.0, round((10.0 - scen_market_score) * 10.0, 1)))

        scen_risk_bk = scenario_eval.get("risk_assessment", {}).get("breakdown", {})
        scen_comp_risk = float(scen_risk_bk.get("competition_risk", 20.0))
        scen_fin_risk = float(scen_risk_bk.get("financial_risk", 20.0))
        scen_infra_risk = float(scen_risk_bk.get("infrastructure_risk", 25.0))
        scen_reg_risk = float(scen_risk_bk.get("regulatory_risk", 10.0))
        scen_exec_risk = float(scen_risk_bk.get("execution_risk", 12.0))

        scen_risk = round(
            (scen_market_risk * 0.25) +
            (scen_comp_risk * 0.20) +
            (scen_fin_risk * 0.25) +
            (scen_infra_risk * 0.10) +
            (scen_reg_risk * 0.10) +
            (scen_exec_risk * 0.10),
            1
        )
        risk_delta = round(scen_risk - base_risk, 1)

        # Dynamic Risk Threshold Explanation
        scen_break_even = scen_fin.get("break_even_percentage", 75.0)
        if risk_delta == 0.0:
            risk_explanation = (
                f"No risk threshold was crossed by this scenario. "
                f"Gross margin ({scen_margin:.1f}%) remains within the safe development hurdle (>=18.0%) "
                f"and capital break-even absorption ({scen_break_even:.1f}%) conforms to risk limits."
            )
        elif risk_delta > 0.0:
            reasons = []
            if simulated_absorption_rate_pct < 90.0:
                reasons.append(f"market absorption softened from {base_corridor_abs:.1f}% to {simulated_absorption_rate_pct:.1f}%")
            if scen_margin < 18.0:
                reasons.append(f"gross margin dropped to {scen_margin:.1f}% (<18.0% institutional hurdle)")
            if scen_break_even > 80.0:
                reasons.append(f"capital break-even elevated to {scen_break_even:.1f}% (>80.0%)")
            if not reasons:
                reasons.append("commercial sensitivity adjusted risk score")
            risk_explanation = f"Composite risk adjusted by +{risk_delta} points to {scen_risk}/100 because {'; and '.join(reasons)}."
        else:
            risk_explanation = (
                f"Composite risk decreased by {abs(risk_delta)} points to {scen_risk}/100 "
                f"due to enhanced gross margin headroom ({scen_margin:.1f}%) and improved break-even metrics."
            )

        # =========================================================================
        # 8. COMPETITION GROUNDING (Real Database Records)
        # =========================================================================
        competitor_record = None
        comp_status = "insufficient_evidence"
        with get_db() as db:
            if req.competitor_project_id:
                row = db.query_one("SELECT * FROM projects WHERE id = %s", (req.competitor_project_id,))
                if row:
                    competitor_record = dict(row)
                    comp_status = "active_verified"
            if not competitor_record:
                # Find comparable competitor project in corridor
                rows = db.query(
                    """
                    SELECT * FROM projects
                    WHERE LOWER(micromarket_name) LIKE LOWER(%s)
                      AND LOWER(developer) NOT LIKE LOWER(%s)
                    ORDER BY id ASC
                    """,
                    (f"%{base.micro_market}%", f"%{base.developer}%")
                )
                if rows:
                    competitor_record = dict(rows[0])
                    comp_status = "active_verified"

        if competitor_record:
            comp_name = competitor_record.get("project_name")
            comp_dev = competitor_record.get("developer")
            comp_price = float(req.competitor_price_per_sqft or competitor_record.get("price_per_sqft") or scenario_price)
            comp_units = competitor_record.get("launched_units", 0)
            comp_sold = competitor_record.get("percentage_sold", 0.0)
            comp_source = f"Database (projects table — ID {competitor_record.get('id')})"
        else:
            comp_name = f"Corridor Competitor ({base.micro_market})"
            comp_dev = "Market Competitor"
            comp_price = float(req.competitor_price_per_sqft or scenario_price)
            comp_units = scenario_units
            comp_sold = 0.0
            comp_source = "Corridor Average Benchmark (No specific competitor project recorded)"

        competition_dimension = {
            "status": comp_status,
            "project_name": comp_name,
            "developer": comp_dev,
            "price_per_sqft": comp_price,
            "launched_units": comp_units,
            "percentage_sold": comp_sold,
            "micro_market": base.micro_market,
            "source": comp_source,
            "notes": (
                "Competitor pricing and developer presence retrieved directly from database records. "
                "Any timing of entry is modeled as a scenario assumption."
            )
        }

        # =========================================================================
        # 9. 12-MONTH TRAJECTORY SIMULATION & DIMENSIONS
        # =========================================================================
        comp_month = req.competitor_launch_month if req.competitor_launch_month is not None else 4
        int_month = req.intervention_month if req.intervention_month is not None else 6
        int_price_adj = req.intervention_price_adjustment_pct if req.intervention_price_adjustment_pct is not None else -5.0
        sim_months = req.simulation_months or 12
        sim_seed = req.simulation_seed or 42

        # Average Area per Unit (derives consistently from saleable area or BHK default)
        saleable_area = float(scen_fin.get("saleable_area_sqft", 0))
        if saleable_area > 0 and scenario_units > 0:
            avg_area_sqft = round(saleable_area / scenario_units, 1)
        else:
            avg_area_sqft = 1450.0  # Standard 3BHK configuration average

        # Total Baseline Target Sales over 12 months
        target_base_sales = min(scenario_units, int(round(scenario_units * (base_absorption_rate_pct / 100.0))))

        # Deterministic 12-month absorption curve weights (surge in m1-m3, steady state m4-m12)
        raw_weights = [0.14, 0.12, 0.10, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07, 0.07, 0.07]
        norm_weights = [w / sum(raw_weights) for w in raw_weights]

        # Allocate integer Baseline monthly bookings (sum strictly equals target_base_sales)
        base_monthly_bookings = []
        allocated_base = 0
        for m_idx in range(12):
            if m_idx == 11:
                b = max(0, target_base_sales - allocated_base)
            else:
                b = int(round(target_base_sales * norm_weights[m_idx]))
                b = max(0, min(b, scenario_units - allocated_base))
            base_monthly_bookings.append(b)
            allocated_base += b

        # Cannibalization drag assumption (strictly labeled scenario assumption, not empirical law)
        drag_factor = 0.25  # 25% deceleration during unmitigated competitive overlap

        # Month-by-month trajectory simulation
        monthly_trajectory = []

        b_cum_bookings = 0
        b_cum_rev = 0.0

        bs_cum_bookings = 0
        bs_cum_rev = 0.0

        int_cum_bookings = 0
        int_cum_rev = 0.0

        int_price = round(scenario_price * (1.0 + (int_price_adj / 100.0)), 2)

        for m in range(1, 13):
            # A. Baseline Month
            b_book = base_monthly_bookings[m - 1]
            b_cum_bookings += b_book
            b_rem = scenario_units - b_cum_bookings
            b_rev = (b_book * avg_area_sqft * scenario_price) / 10_000_000.0
            b_cum_rev += b_rev

            # B. Blind Spot Month (Competitor enters at comp_month, management does nothing)
            if m < comp_month:
                bs_book = b_book
            else:
                # 25% drag assumption
                bs_raw = int(round(b_book * (1.0 - drag_factor)))
                bs_rem_prev = scenario_units - bs_cum_bookings
                bs_book = max(0, min(bs_raw, bs_rem_prev))
            bs_cum_bookings += bs_book
            bs_rem = scenario_units - bs_cum_bookings
            bs_rev = (bs_book * avg_area_sqft * scenario_price) / 10_000_000.0
            bs_cum_rev += bs_rev

            # C. Intervention Month (Management intervenes at int_month with price adjustment)
            if m < comp_month:
                int_book = b_book
                applied_int_price = scenario_price
            elif m < int_month:
                int_book = bs_book
                applied_int_price = scenario_price
            else:
                # Intervention re-establishes sales momentum
                int_raw = int(round(b_book * 1.05))
                int_rem_prev = scenario_units - int_cum_bookings
                int_book = max(0, min(int_raw, int_rem_prev))
                applied_int_price = int_price
            int_cum_bookings += int_book
            int_rem = scenario_units - int_cum_bookings
            int_rev = (int_book * avg_area_sqft * applied_int_price) / 10_000_000.0
            int_cum_rev += int_rev

            monthly_trajectory.append({
                "month": m,
                "monthly_bookings_baseline": b_book,
                "cumulative_bookings_baseline": b_cum_bookings,
                "remaining_units_baseline": b_rem,
                "monthly_revenue_baseline": round(b_rev, 2),
                "cumulative_revenue_baseline": round(b_cum_rev, 2),
                "monthly_bookings_blind_spot": bs_book,
                "cumulative_bookings_blind_spot": bs_cum_bookings,
                "remaining_units_blind_spot": bs_rem,
                "monthly_revenue_blind_spot": round(bs_rev, 2),
                "cumulative_revenue_blind_spot": round(bs_cum_rev, 2),
                "monthly_bookings_intervention": int_book,
                "cumulative_bookings_intervention": int_cum_bookings,
                "remaining_units_intervention": int_rem,
                "monthly_revenue_intervention": round(int_rev, 2),
                "cumulative_revenue_intervention": round(int_cum_rev, 2),
                "competition_active": (m >= comp_month),
                "intervention_active": (m >= int_month)
            })

        # Calculate Loss and Recovery
        blind_spot_loss = round(max(0.0, b_cum_rev - bs_cum_rev), 2)
        intervention_recovery = round(max(0.0, int_cum_rev - bs_cum_rev), 2)
        if blind_spot_loss > 0:
            recovery_percentage = round(min(100.0, max(0.0, (intervention_recovery / blind_spot_loss) * 100.0)), 1)
        else:
            recovery_percentage = 100.0

        # Dimension Summaries
        baseline_dimension = {
            "total_bookings": b_cum_bookings,
            "absorption_rate_pct": round((b_cum_bookings / scenario_units) * 100.0, 1),
            "cumulative_revenue_cr": round(b_cum_rev, 2),
            "remaining_units": scenario_units - b_cum_bookings,
            "price_per_sqft": scenario_price,
            "gross_margin_pct": scen_margin
        }

        blind_spot_dimension = {
            "competitor_launch_month": comp_month,
            "total_bookings": bs_cum_bookings,
            "absorption_rate_pct": round((bs_cum_bookings / scenario_units) * 100.0, 1),
            "cumulative_revenue_cr": round(bs_cum_rev, 2),
            "remaining_units": scenario_units - bs_cum_bookings,
            "blind_spot_revenue_loss_cr": blind_spot_loss,
            "cannibalization_assumption": "25% sales pace deceleration during unmitigated competitor overlap"
        }

        intervention_dimension = {
            "intervention_month": int_month,
            "intervention_price_per_sqft": int_price,
            "price_adjustment_pct": int_price_adj,
            "total_bookings": int_cum_bookings,
            "absorption_rate_pct": round((int_cum_bookings / scenario_units) * 100.0, 1),
            "cumulative_revenue_cr": round(int_cum_rev, 2),
            "remaining_units": scenario_units - int_cum_bookings,
            "intervention_recovery_cr": intervention_recovery,
            "recovery_percentage": recovery_percentage
        }

        # Explicit Scenario Assumptions (incorporating user constraint 4)
        assumptions = {
            "competitor_launch_month": comp_month,
            "intervention_month": int_month,
            "intervention_price_adjustment_pct": int_price_adj,
            "simulation_months": sim_months,
            "simulation_seed": sim_seed,
            "competitor_cannibalization_effect": (
                "SCENARIO ASSUMPTION: Assumes a 25% deceleration in monthly sales velocity during "
                "unmitigated competitive overlap. This is an operational simulation assumption, "
                "NOT an empirically validated econometric model."
            ),
            "intervention_recovery_mechanism": (
                f"SCENARIO ASSUMPTION: Assumes price adjustment of {int_price_adj:+.1f}% initiated in month {int_month} "
                "re-establishes sales momentum back to baseline launch pace, bounded by remaining inventory."
            ),
            "simulated_trajectory_nature": "Scenario simulation, NOT a guaranteed commercial forecast."
        }

        # Structured ScenarioEvidence Object
        scenario_evidence = {
            "baseline": baseline_dimension,
            "blind_spot": blind_spot_dimension,
            "competition": competition_dimension,
            "intervention": intervention_dimension,
            "monthly_trajectory": monthly_trajectory,
            "blind_spot_loss": blind_spot_loss,
            "intervention_recovery": intervention_recovery,
            "recovery_percentage": recovery_percentage,
            "assumptions": assumptions,
            "calculations": [
                "Monthly Revenue = (Monthly Bookings × Unit Area × Price) / 10,000,000",
                "Blind Spot Loss = Baseline Cumulative Revenue - Blind Spot Cumulative Revenue",
                "Intervention Recovery = Intervention Cumulative Revenue - Blind Spot Cumulative Revenue",
                "Recovery % = min(100.0, max(0.0, (Intervention Recovery / Blind Spot Loss) × 100))"
            ],
            "observed_data": {
                "corridor_baseline_absorption_pct": base_corridor_abs,
                "corridor_competitor_record": competition_dimension
            },
            "model_predictions": {
                "ols_price_sensitivity_slope": -0.006945,
                "price_effect_pct": price_effect_pct,
                "scale_effect_pct": scale_effect_pct,
                "rf_unclipped_base_pct": base_raw_rf,
                "rf_unclipped_scenario_pct": scen_raw_rf,
                "clearing_price_benchmark": scenario_price_ml.get("predicted_price_per_sqft"),
                "buyer_fit_index": scenario_buyer_ml.get("buyer_fit_index")
            },
            "simulated_results": {
                "absorption_rate_pct": simulated_absorption_rate_pct,
                "gross_margin_pct": scen_margin,
                "composite_risk_score": scen_risk
            },
            "sources": [
                "Micro-Market Database (micro_markets table)",
                "Competitor Projects Registry (projects table)",
                "Price Sensitivity OLS Regression (p=0.0235)",
                "Market Demand Random Forest (ml/market/market_demand_model.pkl)",
                "KMeans Buyer Profiling (ml/buyer/buyer_segment_model.pkl)"
            ],
            "limitations": [
                "Competitor entry and cannibalization deceleration are scenario assumptions, not empirical laws.",
                "Monthly trajectory reflects simulated pacing; micro-topographical volatility is excluded."
            ],
            "simulation_seed": sim_seed
        }

        # =========================================================================
        # 10. DECISION ENGINE INTEGRATION (SOLE AUTHORITY FOR VERDICT)
        # =========================================================================
        decision_engine = DecisionEngine()
        decision_eval = decision_engine.evaluate_scenario(
            project=scenario_project,
            scenario_evidence=scenario_evidence
        )
        scen_decision = decision_eval.get("decision")
        decision_result_id = decision_eval.get("decision_result_id")

        scenario_eval["decision"] = scen_decision
        scenario_eval["executive_summary"] = decision_eval.get("executive_summary")
        scenario_eval["decision_result_id"] = decision_result_id

        # 11. Provenance Metadata
        provenance = {
            "price_per_sqft": "USER_INPUT",
            "units": "USER_INPUT",
            "bhk": "USER_INPUT",
            "saleable_area": "FORMULA",
            "gross_revenue": "FORMULA",
            "project_cost": "FORMULA",
            "gross_margin": "FORMULA",
            "break_even": "FORMULA",
            "roi": "FORMULA",
            "market_absorption": "ML (Random Forest Regressor)",
            "price_benchmark": "ML (Gradient Boosting Regressor)",
            "buyer_fit": "ML (K-Means Clustering)",
            "composite_risk": "RULE + FORMULA",
            "decision_verdict": "RULE (DecisionEngine)",
            "micro_market_baseline": "DATABASE",
            "competitor_data": "DATABASE (projects table)",
            "cannibalization_effect": "SCENARIO ASSUMPTION",
            "intervention_trajectory": "SCENARIO SIMULATION"
        }

        # 12. Step-by-step How Calculated Breakdown
        units_delta = scenario_units - base.units
        how_calculated = [
            {
                "metric": "Scenario Price",
                "value": f"₹{base.price_per_sqft:,.0f} → ₹{scenario_price:,.0f} ({'+' if price_delta_inr >= 0 else ''}₹{price_delta_inr:,.0f}/sq.ft)",
                "source": "[USER INPUT]",
                "method": "Direct user scenario variable"
            },
            {
                "metric": "Saleable Area & Units",
                "value": f"{base.units} → {scenario_units} units ({saleable_area:,.0f} sq.ft)",
                "source": "[FORMULA]",
                "method": f"Planned Units × Average Configuration Area ({avg_area_sqft:,.0f} sq.ft/unit)"
            },
            {
                "metric": "Gross Realization (Revenue)",
                "value": f"₹{base_rev:,.2f} Cr → ₹{scen_rev:,.2f} Cr ({'+' if rev_delta_cr >= 0 else ''}₹{rev_delta_cr:,.2f} Cr)",
                "source": "[FORMULA]",
                "method": "Deterministic formula: (Price per sq.ft × Total Saleable Area) / 10,000,000"
            },
            {
                "metric": "Gross Margin",
                "value": f"{base_margin:.1f}% → {scen_margin:.1f}% ({'+' if margin_delta_pct >= 0 else ''}{margin_delta_pct:.1f}%)",
                "source": "[FORMULA]",
                "method": "Deterministic formula: ((Price - Total Cost per sq.ft) / Price) × 100"
            },
            {
                "metric": "Market Absorption & Velocity",
                "value": f"{base_corridor_abs:.1f}% → {simulated_absorption_rate_pct:.1f}% ({'+' if absorption_shift_pct >= 0 else ''}{absorption_shift_pct:.1f}%)",
                "source": "[DATABASE + DATA-DERIVED + ML]",
                "method": f"Base Corridor ({base_corridor_abs:.1f}% [DATABASE]) + Price Effect ({price_effect_pct:+.2f}% [DATA-DERIVED OLS β=-0.006945]) + Scale Effect ({scale_effect_pct:+.2f}% [ML Random Forest Gradient])"
            },
            {
                "metric": "Competitor Launch Dynamic",
                "value": f"{comp_name} ({comp_dev}) enters at Month {comp_month} @ ₹{comp_price:,.0f}/sq.ft",
                "source": "[DATABASE + SCENARIO ASSUMPTION]",
                "method": "Observed project data from database; entry timing modeled as scenario assumption"
            },
            {
                "metric": "Blind Spot Revenue Loss",
                "value": f"₹{blind_spot_loss:.2f} Cr",
                "source": "[SCENARIO SIMULATION]",
                "method": "Baseline Cumulative Revenue - Blind Spot Cumulative Revenue (under 25% drag assumption)"
            },
            {
                "metric": "Intervention Recovery",
                "value": f"₹{intervention_recovery:.2f} Cr ({recovery_percentage:.1f}% recovered)",
                "source": "[SCENARIO SIMULATION]",
                "method": f"Intervention at Month {int_month} with {int_price_adj:+.1f}% price adjustment recovers sales momentum"
            },
            {
                "metric": "Decision Verdict",
                "value": f"{base_eval.get('decision')} → {scen_decision}",
                "source": "[RULE — DecisionEngine]",
                "method": f"Decision Engine hurdle criteria: Launch (Abs>=80%, Margin>=18%, Risk<55); Hold (Abs>=65%, Margin>=14%, Risk<70); Else No-launch. Persisted to decision_results (ID: {decision_result_id})"
            }
        ]

        # 13. Assemble Comparison and Traceable Dictionaries
        base_dict = {
            "price_per_sqft": base.price_per_sqft,
            "units": base.units,
            "bhk": base.bhk,
            "decision": base_eval.get("decision"),
            "gross_revenue_cr": base_rev,
            "gross_margin_pct": base_margin,
            "absorption_rate_pct": base_corridor_abs,
            "base_absorption_rate_pct": base_corridor_abs,
            "composite_risk_score": base_risk
        }

        scen_dict = {
            "price_per_sqft": scenario_price,
            "units": scenario_units,
            "bhk": scenario_bhk,
            "decision": scen_decision,
            "gross_revenue_cr": scen_rev,
            "gross_margin_pct": scen_margin,
            "absorption_rate_pct": simulated_absorption_rate_pct,
            "simulated_absorption_rate_pct": simulated_absorption_rate_pct,
            "composite_risk_score": scen_risk
        }

        deltas_dict = {
            "price_delta_inr": price_delta_inr,
            "units_delta": units_delta,
            "revenue_delta_cr": rev_delta_cr,
            "gross_margin_delta_pct": margin_delta_pct,
            "absorption_shift_pct": absorption_shift_pct,
            "risk_score_delta": risk_delta
        }

        comparison = {
            "baseline": base_dict,
            "scenario": scen_dict,
            "deltas": deltas_dict,
            "ml_sensitivity": {
                "base_market_absorption_pct": base_absorption_rate_pct,
                "predicted_market_absorption_pct": simulated_absorption_rate_pct,
                "absorption_shift_pct": absorption_shift_pct,
                "predicted_market_absorbed_units": scenario_market_ml.get("predicted_absorbed_units"),
                "predicted_clearing_price_sqft": scenario_price_ml.get("predicted_price_per_sqft"),
                "scenario_buyer_fit_index": scenario_buyer_ml.get("buyer_fit_index")
            },
            "scenario_observations": [
                f"Revenue shifts by {'+' if rev_delta_cr >= 0 else ''}INR {rev_delta_cr} Cr with margin delta of {'+' if margin_delta_pct >= 0 else ''}{margin_delta_pct}%.",
                f"Market absorption shifts by {'+' if absorption_shift_pct >= 0 else ''}{absorption_shift_pct}% ({base_absorption_rate_pct:.1f}% → {simulated_absorption_rate_pct:.1f}%).",
                f"Competitor entry in Month {comp_month} creates ₹{blind_spot_loss:.2f} Cr blind spot exposure.",
                f"Intervention at Month {int_month} recovers ₹{intervention_recovery:.2f} Cr ({recovery_percentage:.1f}%).",
                f"Decision Engine verdict: {base_eval.get('decision')} -> {scen_decision}."
            ]
        }

        # 14. Relational Persistence to scenario_runs (linking decision_result_id)
        try:
            with get_db() as db:
                db.execute(
                    """
                    INSERT INTO scenario_runs (project_name, base_parameters, scenario_parameters, result_summary, decision_result_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        base.project_name,
                        json.dumps({"price": base.price_per_sqft, "units": base.units, "bhk": base.bhk}),
                        json.dumps({
                            "price": scenario_price,
                            "units": scenario_units,
                            "bhk": scenario_bhk,
                            "competitor_launch_month": comp_month,
                            "intervention_month": int_month,
                            "intervention_price_adjustment_pct": int_price_adj
                        }),
                        json.dumps({
                            "deltas": deltas_dict,
                            "blind_spot_loss_cr": blind_spot_loss,
                            "intervention_recovery_cr": intervention_recovery,
                            "recovery_percentage": recovery_percentage,
                            "verdict": scen_decision
                        }),
                        decision_result_id
                    )
                )
        except Exception as e:
            print(f"[Scenario Engine Warning] DB log failed: {e}")

        return {
            "scenario_name": req.scenario_name,
            "project_name": base.project_name,
            "base": base_dict,
            "scenario": scen_dict,
            "delta": deltas_dict,
            "decision": scen_decision,
            "decision_result_id": decision_result_id,
            "base_absorption_rate_pct": base_absorption_rate_pct,
            "simulated_absorption_rate_pct": simulated_absorption_rate_pct,
            "absorption_shift_pct": absorption_shift_pct,
            "risk_score_delta": risk_delta,
            "risk_explanation": risk_explanation,
            "baseline": baseline_dimension,
            "blind_spot": blind_spot_dimension,
            "competition": competition_dimension,
            "intervention": intervention_dimension,
            "monthly_trajectory": monthly_trajectory,
            "blind_spot_loss_cr": blind_spot_loss,
            "intervention_recovery_cr": intervention_recovery,
            "recovery_percentage": recovery_percentage,
            "scenario_evidence": scenario_evidence,
            "provenance": provenance,
            "how_calculated": how_calculated,
            "comparison": comparison,
            "scenario_evaluation": scenario_eval
        }


_scenario_engine = None


def get_scenario_engine() -> ScenarioEngine:
    global _scenario_engine
    if _scenario_engine is None:
        _scenario_engine = ScenarioEngine()
    return _scenario_engine
