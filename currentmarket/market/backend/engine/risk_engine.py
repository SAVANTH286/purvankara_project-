from typing import Dict, Any, List
from backend.agents.base import ProjectInput, AgentEvidence


class RiskEngine:
    def __init__(self):
        pass

    def evaluate(self, project: ProjectInput, evidence: Dict[str, AgentEvidence]) -> Dict[str, Any]:
        market_ev = evidence.get("market")
        comp_ev = evidence.get("competition")
        fin_ev = evidence.get("finance")
        infra_ev = evidence.get("infrastructure")
        reg_ev = evidence.get("regulatory")
        exec_ev = evidence.get("execution")

        # 1. Market Risk (0-100, lower is better)
        market_score = market_ev.score if market_ev else 7.5
        market_risk = max(5.0, min(95.0, round((10.0 - market_score) * 10.0, 1)))

        # 2. Competition Risk
        comp_score = comp_ev.score if comp_ev else 7.5
        comp_risk = max(10.0, min(90.0, round((10.0 - comp_score) * 10.0, 1)))

        # 3. Financial Risk
        margin = 22.0
        break_even = 75.0
        if fin_ev and fin_ev.metrics:
            margin = fin_ev.metrics.get("gross_margin_pct", 22.0)
            break_even = fin_ev.metrics.get("break_even_percentage", 75.0)

        fin_risk = 20.0
        if margin < 15.0:
            fin_risk += 40.0
        elif margin < 20.0:
            fin_risk += 20.0
        if break_even > 80.0:
            fin_risk += 25.0
        fin_risk = max(10.0, min(95.0, round(fin_risk, 1)))

        # 4. Infrastructure Risk (Safe None handling)
        flood_score = None
        if infra_ev and infra_ev.metrics:
            flood_score = infra_ev.metrics.get("flood_risk_score")
        
        if flood_score is not None:
            infra_risk = max(10.0, min(90.0, round(float(flood_score) * 18.0, 1)))
        else:
            # Default moderate baseline when flood telemetry is unassessed
            infra_risk = 25.0

        # 5. Regulatory Risk
        reg_score = reg_ev.score if reg_ev else 9.0
        reg_risk = max(5.0, min(90.0, round((10.0 - reg_score) * 10.0, 1)))

        # 6. Execution Risk
        exec_score = exec_ev.score if exec_ev else 8.0
        exec_risk = max(10.0, min(90.0, round((10.0 - exec_score) * 10.0, 1)))

        # Weighted Composite Risk Index
        composite_risk = round(
            (market_risk * 0.25) +
            (comp_risk * 0.20) +
            (fin_risk * 0.25) +
            (infra_risk * 0.10) +
            (reg_risk * 0.10) +
            (exec_risk * 0.10),
            1
        )

        if composite_risk < 35.0:
            level = "Low Risk"
            summary = "Overall project and micro-market risk profile is low and within healthy development tolerances."
        elif composite_risk < 60.0:
            level = "Moderate Risk"
            summary = "Manageable risk exposure with specific operational items requiring active monitoring."
        else:
            level = "Elevated Risk"
            summary = "Elevated composite risk detected across absorption velocity, competitor density, or financial margins."

        factors = []
        if market_risk > 40:
            factors.append("Micro-market absorption velocity requires phased inventory release.")
        if comp_risk > 40:
            factors.append("Active peer developer supply pipeline in immediate vicinity.")
        if fin_risk > 40:
            factors.append("Development margins are sensitive to cost escalation.")
        if not factors:
            factors.append("Project attributes conform to optimal launch risk thresholds.")

        return {
            "composite_risk_score": composite_risk,
            "risk_level": level,
            "risk_status": "partially_assessed" if flood_score is None else "assessed",
            "summary": summary,
            "breakdown": {
                "market_risk": market_risk,
                "competition_risk": comp_risk,
                "financial_risk": fin_risk,
                "infrastructure_risk": infra_risk,
                "regulatory_risk": reg_risk,
                "execution_risk": exec_risk
            },
            "risk_factors": factors,
            "project_specific_note": "Project-specific risk is evaluated on proposed project scale, micro-market absorption, and developer execution tier."
        }
