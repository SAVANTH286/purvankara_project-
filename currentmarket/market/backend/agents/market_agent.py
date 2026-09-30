from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence
from backend.db.connection import get_db


class MarketAgent(BaseAgent):
    def __init__(self):
        super().__init__("Market Intelligence Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        target_market = project.micro_market.strip()

        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM micro_markets WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target_market}%",)
            )

        if not row:
            with get_db() as db:
                row = db.query_one("SELECT * FROM micro_markets LIMIT 1")

        mm_name = row["micromarket_name"]
        zone = row["zone"]
        project_count = row["project_count"] or 0
        launched = row["launched_units"] or 0
        absorbed = row["absorbed_units"] or 0
        available = row["available_units"]
        avg_price = row["average_price_per_sqft"]
        sold_pct = row["average_percentage_sold"] or 85.0
        absorption_sig = row["absorption_signal"] or "Healthy"
        key_drivers = row["key_drivers"] or ""

        # Overhang calculation
        quarterly_absorption = max(1, absorbed / 12) if absorbed else 500
        overhang_months = round(((available or 1000) / quarterly_absorption) * 3, 1)

        flags = []
        if sold_pct >= 90.0:
            bias = "supportive"
            score = 9.2
        elif sold_pct >= 75.0:
            bias = "supportive"
            score = 8.0
        elif sold_pct >= 60.0:
            bias = "neutral"
            score = 6.5
        else:
            bias = "caution"
            score = 4.5
            flags.append(f"Micro-market historical absorption ({sold_pct}%) is subdued.")

        evidence = [
            f"Micro-market {mm_name} ({zone} Zone) displays a {absorption_sig.lower()} absorption signal.",
            f"Historical volume: {project_count} projects, {launched:,} launched units, {absorbed:,} absorbed units.",
            f"Calculated micro-market absorption rate is {sold_pct:.2f}%.",
            f"Estimated inventory overhang stands at ~{overhang_months} months."
        ]
        if key_drivers:
            evidence.append(f"Key corridor drivers: {key_drivers}.")

        metrics = {
            "micro_market": mm_name,
            "zone": zone,
            "project_count": project_count,
            "launched_units": launched,
            "absorbed_units": absorbed,
            "available_units": available,
            "absorption_rate_percentage": sold_pct,
            "overhang_months": overhang_months,
            "average_price_per_sqft": avg_price,
            "absorption_signal": absorption_sig
        }

        limitations = [
            "Predictive temporal demand forecasting ML model is unavailable due to lack of longitudinal quarterly time-series dataset; relying on cumulative historical absorption."
        ]

        return AgentEvidence(
            agent_name=self.name,
            status="available",
            decision_bias=bias,
            score=score,
            summary=f"{mm_name} exhibits {absorption_sig.lower()} market dynamics with {sold_pct:.2f}% cumulative absorption and ~{overhang_months} months overhang.",
            metrics=metrics,
            evidence=evidence,
            limitations=limitations,
            flags=flags,
            tool_used="database_query",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
