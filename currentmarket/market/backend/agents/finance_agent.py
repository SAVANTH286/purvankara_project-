from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence


class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Financial Feasibility Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        price = project.price_per_sqft
        units = project.units
        segment = project.property_segment.lower()

        # Average unit size based on BHK
        bhk_str = (project.bhk or "3BHK").upper()
        if "1BHK" in bhk_str:
            avg_sqft = 650.0
        elif "2BHK" in bhk_str:
            avg_sqft = 1050.0
        elif "4BHK" in bhk_str:
            avg_sqft = 2200.0
        else:
            avg_sqft = 1450.0  # default 3BHK

        total_saleable_sqft = units * avg_sqft

        user_provided_costs = bool(project.construction_cost_per_sqft and project.land_cost_per_sqft)

        # Construction cost
        if project.construction_cost_per_sqft:
            construction_cost = float(project.construction_cost_per_sqft)
        else:
            if "luxury" in segment or "high-end" in segment:
                construction_cost = 4200.0
            elif "premium" in segment or "mid-high" in segment:
                construction_cost = 3600.0
            else:
                construction_cost = 3100.0

        # Land cost
        if project.land_cost_per_sqft:
            land_cost = float(project.land_cost_per_sqft)
        else:
            land_cost = price * 0.25

        soft_costs = construction_cost * 0.14
        total_cost_per_sqft = construction_cost + land_cost + soft_costs

        total_project_cost_cr = round((total_cost_per_sqft * total_saleable_sqft) / 10000000.0, 2)
        total_gross_revenue_cr = round((price * total_saleable_sqft) / 10000000.0, 2)
        gross_profit_cr = round(total_gross_revenue_cr - total_project_cost_cr, 2)
        gross_margin_pct = round(((price - total_cost_per_sqft) / price) * 100.0, 1)

        break_even_pct = round((total_cost_per_sqft / price) * 100.0, 1)
        break_even_units = int(units * (break_even_pct / 100.0))
        projected_roi_pct = round((gross_profit_cr / total_project_cost_cr) * 100.0, 1) if total_project_cost_cr else 0.0

        flags = []
        if gross_margin_pct < 15.0:
            bias = "caution"
            score = 4.8
            flags.append(f"Compressed gross margin ({gross_margin_pct}% < 15% hurdle rate).")
        elif gross_margin_pct >= 24.0:
            bias = "supportive"
            score = 9.0
        else:
            bias = "supportive"
            score = 7.8

        if break_even_pct > 80.0:
            flags.append(f"Elevated break-even threshold ({break_even_pct}% sales needed).")

        evidence = [
            f"Projected Gross Realization: INR {total_gross_revenue_cr:,.2f} Cr across {total_saleable_sqft:,.0f} sq.ft saleable area.",
            f"Estimated Total Development Cost: INR {total_project_cost_cr:,.2f} Cr (INR {total_cost_per_sqft:,.0f}/sq.ft).",
            f"Projected Gross Margin: {gross_margin_pct}% with estimated ROI of {projected_roi_pct}%.",
            f"Capital Break-Even requires absorbing {break_even_units} of {units} units ({break_even_pct}% inventory)."
        ]

        metrics = {
            "saleable_area_sqft": total_saleable_sqft,
            "realization_per_sqft": price,
            "total_cost_per_sqft": round(total_cost_per_sqft, 2),
            "construction_cost_sqft": construction_cost,
            "land_cost_sqft": land_cost,
            "gross_revenue_cr": total_gross_revenue_cr,
            "total_cost_cr": total_project_cost_cr,
            "gross_profit_cr": gross_profit_cr,
            "gross_margin_pct": gross_margin_pct,
            "projected_roi_pct": projected_roi_pct,
            "break_even_units": break_even_units,
            "break_even_percentage": break_even_pct,
            "user_provided_costs": user_provided_costs
        }

        if user_provided_costs:
            status = "available"
            limitations = [
                "Financial projections rely on user-supplied construction and land acquisition parameters."
            ]
        else:
            status = "partial"
            limitations = [
                "Land acquisition and construction costs were not provided in project input; figures are benchmark estimates, marking financial assessment as provisional."
            ]

        return AgentEvidence(
            agent_name=self.name,
            status=status,
            decision_bias=bias,
            score=score,
            summary=f"Financial viability: {gross_margin_pct}% gross margin, INR {gross_profit_cr} Cr gross profit, {break_even_pct}% break-even threshold.",
            metrics=metrics,
            evidence=evidence,
            limitations=limitations,
            flags=flags,
            tool_used="cost_model_calculation",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
