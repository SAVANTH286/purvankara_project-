from typing import Dict, Any, List, Optional
from backend.agents.base import ProjectInput, AgentEvidence


class DecisionEngine:
    def __init__(self):
        pass

    @staticmethod
    def determine_verdict(absorption_pct: float, gross_margin_pct: float, composite_risk: float) -> str:
        """
        Deterministic Decision Engine rules:
        - Launch: Absorption >= 80% AND Margin >= 18% AND Risk < 55
        - Hold: Absorption >= 65% AND Margin >= 14% AND Risk < 70
        - Otherwise: No-launch
        """
        if absorption_pct >= 80.0 and gross_margin_pct >= 18.0 and composite_risk < 55.0:
            return "Launch"
        elif absorption_pct >= 65.0 and gross_margin_pct >= 14.0 and composite_risk < 70.0:
            return "Hold"
        else:
            return "No-launch"

    def evaluate(
        self,
        project: ProjectInput,
        evidence: Dict[str, AgentEvidence],
        risk_profile: Dict[str, Any],
        absorption_rate_pct: Optional[float] = None,
        gross_margin_pct: Optional[float] = None,
        composite_risk_score: Optional[float] = None
    ) -> Dict[str, Any]:
        market_ev = evidence.get("market")
        comp_ev = evidence.get("competition")
        fin_ev = evidence.get("finance")
        buyer_ev = evidence.get("buyer")
        loc_ev = evidence.get("location")
        infra_ev = evidence.get("infrastructure")
        reg_ev = evidence.get("regulatory")
        exec_ev = evidence.get("execution")
        port_ev = evidence.get("portfolio")

        # 1. Scoring inputs (support scenario overrides when evaluating what-if runs)
        sold_pct = 85.0
        if absorption_rate_pct is not None:
            sold_pct = float(absorption_rate_pct)
        elif market_ev and market_ev.metrics:
            sold_pct = float(market_ev.metrics.get("absorption_rate_percentage", 85.0))

        gross_margin = 22.0
        user_provided_costs = False
        if gross_margin_pct is not None:
            gross_margin = float(gross_margin_pct)
            if fin_ev and fin_ev.metrics:
                user_provided_costs = fin_ev.metrics.get("user_provided_costs", False)
        elif fin_ev and fin_ev.metrics:
            gross_margin = float(fin_ev.metrics.get("gross_margin_pct", 22.0))
            user_provided_costs = fin_ev.metrics.get("user_provided_costs", False)

        composite_risk = 30.0
        if composite_risk_score is not None:
            composite_risk = float(composite_risk_score)
        elif risk_profile:
            composite_risk = float(risk_profile.get("composite_risk_score", 30.0))

        positive_drivers = []
        cautionary_flags = []
        recommendations = []

        # Evaluate Drivers
        if sold_pct >= 80.0:
            positive_drivers.append(f"Strong micro-market absorption velocity ({sold_pct:.1f}% cumulative sales).")
        if gross_margin >= 20.0:
            positive_drivers.append(f"Healthy financial headroom with {gross_margin:.1f}% projected gross margin.")
        if loc_ev and loc_ev.score >= 7.5:
            positive_drivers.append(f"Favorable location connectivity to primary {project.micro_market} employment corridor.")
        if buyer_ev and buyer_ev.ml_used:
            predicted_seg = buyer_ev.metrics.get("predicted_segment", "Corporate Professionals")
            positive_drivers.append(f"Strong buyer alignment with demographic segment '{predicted_seg}' ({project.bhk}).")
        if infra_ev and infra_ev.score >= 7.0:
            positive_drivers.append("Operational rapid transit and arterial road connectivity verified.")
        if exec_ev and exec_ev.score >= 8.0:
            positive_drivers.append(f"Strong execution governance under {project.developer} institutional pedigree.")

        # Evaluate Flags
        bhk_cov = "sufficient"
        comparable_count = 0
        if comp_ev and comp_ev.metrics:
            bhk_cov = comp_ev.metrics.get("bhk_coverage_status", "insufficient")
            comparable_count = comp_ev.metrics.get("comparable_project_count", 0)

        if bhk_cov == "insufficient":
            cautionary_flags.append(f"BHK-specific comparable data for {project.bhk} is currently unrecorded.")
        if comparable_count >= 18:
            cautionary_flags.append(f"Active competitor presence ({comparable_count} comparable projects).")
        if gross_margin < 18.0:
            cautionary_flags.append(f"Gross margin ({gross_margin:.1f}%) is below preferred 20% hurdle rate.")
        if sold_pct < 65.0:
            cautionary_flags.append(f"Subdued absorption velocity ({sold_pct:.1f}%) presents market demand risk.")

        # Provisional flag check
        decision_is_provisional = False
        provisional_reasons = []
        if not user_provided_costs:
            decision_is_provisional = True
            provisional_reasons.append("Project financial metrics rely on industry cost benchmarks rather than site-specific construction/land contracts.")
        if bhk_cov == "insufficient":
            decision_is_provisional = True
            provisional_reasons.append("Historical comparable projects lack granular unit-level BHK pricing records.")

        # Core Decision Logic (Strictly Launch, Hold, or No-launch)
        decision = self.determine_verdict(sold_pct, gross_margin, composite_risk)

        if decision == "Launch":
            executive_summary = (
                f"The investment committee recommends an affirmative LAUNCH for {project.project_name}. "
                f"Micro-market demand dynamics in {project.micro_market} are robust ({sold_pct:.1f}% absorption), "
                f"financial margins are viable ({gross_margin:.1f}%), and developer execution track record is solid."
            )
            recommendations.append("Proceed with Phase 1 pre-launch marketing campaign and customer expression of interest (EOI).")
            recommendations.append(f"Structure launch volume at ~{int(project.units * 0.4)} units for initial tranche release.")
            recommendations.append("Maintain strict milestone monitoring against competitor launch calendars.")

        elif decision == "Hold":
            executive_summary = (
                f"A conditional HOLD is advised for {project.project_name}. While fundamental micro-market indicators "
                f"are acceptable, specific commercial or unit-level variables warrant risk mitigation prior to capital commitment."
            )
            recommendations.append(f"Conduct targeted primary buyer pricing survey on {project.bhk} unit economics.")
            recommendations.append("Re-evaluate contractor procurement packages to improve gross margin towards the 20% benchmark.")
            recommendations.append("Align launch date to coincide with upcoming corridor transit milestones.")

        else:
            executive_summary = (
                f"A NO-LAUNCH determination has been reached for {project.project_name}. "
                f"Current realization economics ({gross_margin:.1f}% margin) or absorption constraints ({sold_pct:.1f}% absorption) "
                f"in {project.micro_market} present elevated downside risk."
            )
            recommendations.append("Rework land acquisition terms or explore joint development restructuring.")
            recommendations.append("Re-evaluate product segmentation or pivot to alternative residential unit configurations.")

        # Clean, factual observations conforming strictly to Step 1 & Rule 24
        observations = []

        # Market observation
        if sold_pct >= 85.0:
            observations.append(
                f"The micro-market source contains a positive absorption signal ({sold_pct:.2f}% calculated absorption)."
            )
        else:
            observations.append("The micro-market source contains a moderate absorption signal.")

        # Competition observations
        if comparable_count > 0:
            observations.append(
                f"{comparable_count} historical comparable projects were identified for the supplied property type "
                f"and segment within the selected micro-market."
            )
        else:
            observations.append("No historical comparable projects were identified using the supplied property type and segment.")

        if bhk_cov == "insufficient":
            observations.append(
                f"BHK-specific comparison for {project.bhk} is unavailable because the comparable projects do not "
                "contain sufficient known BHK data."
            )

        observations.append("Comparable-project price evidence is insufficient for a price comparison.")

        # Buyer intelligence observation
        if project.include_buyer_intelligence:
            observations.append("Buyer Intelligence was included as historical buyer-pattern evidence only.")
        else:
            observations.append("Buyer Intelligence was disabled by the user.")

        # Risk observation
        observations.append(risk_profile.get("project_specific_note", "Project-specific risk is evaluated on proposed project scale, micro-market absorption, and developer execution tier."))

        return {
            "decision": decision,
            "decision_is_provisional": decision_is_provisional,
            "provisional_reasons": provisional_reasons,
            "confidence": None,  # Strictly null as required by Rule 24 (no fake confidence numbers)
            "executive_summary": executive_summary,
            "positive_drivers": positive_drivers,
            "cautionary_flags": cautionary_flags,
            "recommended_actions": recommendations,
            "observations": observations
        }

    def evaluate_scenario(
        self,
        project: ProjectInput,
        scenario_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Official Decision Engine scenario evaluation.
        The Decision Engine is the SOLE authority for verdicts (Launch, Hold, No-launch).
        Applies standard institutional hurdle criteria to scenario-derived metrics:
        - Launch: absorption >= 80% AND gross_margin >= 18% AND composite_risk < 55
        - Hold: absorption >= 65% AND gross_margin >= 14% AND composite_risk < 70
        - Otherwise: No-launch

        Persists decision to decision_results and granular evidence to decision_evidence.
        Returns the verdict and audit record ID.
        """
        from backend.db.connection import get_db

        scen_metrics = scenario_evidence.get("simulated_results", {})
        absorption_pct = float(scen_metrics.get("absorption_rate_pct", 80.0))
        gross_margin_pct = float(scen_metrics.get("gross_margin_pct", 20.0))
        composite_risk = float(scen_metrics.get("composite_risk_score", 45.0))

        # SOLE authority for verdict - preserves strict hurdle rules
        verdict = self.determine_verdict(
            absorption_pct=absorption_pct,
            gross_margin_pct=gross_margin_pct,
            composite_risk=composite_risk
        )

        positive_drivers = []
        cautionary_flags = []
        recommendations = []

        blind_spot_loss = float(scenario_evidence.get("blind_spot_loss", 0.0))
        intervention_recovery = float(scenario_evidence.get("intervention_recovery", 0.0))
        recovery_pct = float(scenario_evidence.get("recovery_percentage", 0.0))
        comp_month = scenario_evidence.get("assumptions", {}).get("competitor_launch_month", 4)
        int_month = scenario_evidence.get("assumptions", {}).get("intervention_month", 6)

        if absorption_pct >= 80.0:
            positive_drivers.append(f"Strong simulated absorption velocity ({absorption_pct:.1f}% cumulative sales).")
        if gross_margin_pct >= 18.0:
            positive_drivers.append(f"Financial margin ({gross_margin_pct:.1f}%) meets development hurdle rate (>=18%).")
        if intervention_recovery > 0:
            positive_drivers.append(
                f"Management intervention strategy recovers ₹{intervention_recovery:.2f} Cr ({recovery_pct:.1f}% of blind spot loss)."
            )

        if blind_spot_loss > 0:
            cautionary_flags.append(
                f"Competitor entry in Month {comp_month} creates a potential blind spot revenue exposure of ₹{blind_spot_loss:.2f} Cr if unmitigated."
            )
        if gross_margin_pct < 18.0:
            cautionary_flags.append(f"Simulated gross margin ({gross_margin_pct:.1f}%) compresses below the 18% preferred benchmark.")
        if absorption_pct < 65.0:
            cautionary_flags.append(f"Simulated absorption velocity ({absorption_pct:.1f}%) presents market demand risk.")
        if composite_risk >= 55.0:
            cautionary_flags.append(f"Composite scenario risk ({composite_risk:.1f}/100) requires proactive risk containment.")

        if verdict == "Launch":
            executive_summary = (
                f"The investment committee recommends an affirmative LAUNCH for {project.project_name}. "
                f"Scenario absorption is robust ({absorption_pct:.1f}%), gross margin ({gross_margin_pct:.1f}%) "
                f"meets hurdle requirements, and composite risk ({composite_risk:.1f}/100) is controlled."
            )
            recommendations.append("Proceed with Phase 1 launch planning.")
            if blind_spot_loss > 0:
                recommendations.append(f"Prepare pre-approved counter-incentive protocol for competitor entry in Month {comp_month}.")
        elif verdict == "Hold":
            executive_summary = (
                f"A conditional HOLD is advised for {project.project_name}. "
                f"While baseline viability exists, scenario dynamics (absorption: {absorption_pct:.1f}%, margin: {gross_margin_pct:.1f}%) "
                f"warrant commercial de-risking prior to capital commitment."
            )
            recommendations.append("Execute targeted buyer pricing survey to protect realization margins.")
            recommendations.append("Review construction procurement packages to expand margin buffer.")
        else:
            executive_summary = (
                f"A NO-LAUNCH determination has been reached for {project.project_name}. "
                f"Simulated realization ({gross_margin_pct:.1f}% margin), absorption ({absorption_pct:.1f}%), "
                f"or composite risk ({composite_risk:.1f}/100) fail institutional hurdle criteria."
            )
            recommendations.append("Rework land acquisition terms or adjust configuration density.")
            recommendations.append("Restructure development parameters before resubmission to investment committee.")

        # Relational Persistence into decision_results & decision_evidence
        decision_result_id = None
        try:
            with get_db() as db:
                decision_result_id = db.execute_insert(
                    """
                    INSERT INTO decision_results (project_name, decision, decision_engine_version, scenario_considered, executive_summary)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        project.project_name,
                        verdict,
                        "v2.5-hurdle",
                        1,
                        executive_summary
                    )
                )

                if decision_result_id:
                    evidence_items = [
                        ("scenario", "simulated_absorption_pct", f"{absorption_pct:.2f}%", "Simulated cumulative absorption rate", "Scenario Engine", "INFO"),
                        ("scenario", "simulated_gross_margin_pct", f"{gross_margin_pct:.2f}%", "Simulated gross margin", "Scenario Engine", "INFO" if gross_margin_pct >= 18 else "WARNING"),
                        ("scenario", "composite_risk_score", f"{composite_risk:.1f}", "Re-evaluated scenario risk score", "Risk Engine", "INFO" if composite_risk < 55 else "WARNING"),
                        ("scenario", "blind_spot_loss_cr", f"INR {blind_spot_loss:.2f} Cr", "Revenue loss if competitor enters without counter-action", "Blind Spot Simulation", "WARNING" if blind_spot_loss > 0 else "INFO"),
                        ("scenario", "intervention_recovery_cr", f"INR {intervention_recovery:.2f} Cr", "Revenue recovered via management intervention", "Intervention Simulation", "INFO"),
                        ("scenario", "recovery_percentage", f"{recovery_pct:.1f}%", "Percentage of blind spot revenue loss recovered", "Intervention Simulation", "INFO")
                    ]
                    for cat, factor, val, interp, src, sev in evidence_items:
                        db.execute(
                            """
                            INSERT INTO decision_evidence (decision_result_id, category, factor, value, interpretation, source, severity)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (decision_result_id, cat, factor, val, interp, src, sev)
                        )
        except Exception as e:
            print(f"[Decision Engine Warning] Failed to persist decision results: {e}")

        return {
            "decision": verdict,
            "decision_result_id": decision_result_id,
            "decision_engine_version": "v2.5-hurdle",
            "executive_summary": executive_summary,
            "positive_drivers": positive_drivers,
            "cautionary_flags": cautionary_flags,
            "recommended_actions": recommendations,
            "hurdle_criteria": {
                "launch": "Absorption >= 80% AND Margin >= 18% AND Risk < 55",
                "hold": "Absorption >= 65% AND Margin >= 14% AND Risk < 70",
                "no_launch": "Fails hurdle thresholds"
            }
        }

