from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence


class ExecutionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Project Execution Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        developer = project.developer.strip()
        units = project.units

        # Reputed / Tier 1 developers have institutional delivery systems
        is_tier_1 = any(
            t in developer.lower()
            for t in ["puravankara", "purva", "prestige", "brigade", "sobha", "godrej", "tata", "total environment"]
        )

        if is_tier_1:
            execution_rating = 8.8
            bias = "supportive"
            tier = "Tier-1 Institutional Developer"
            summary = f"{developer} has established institutional delivery governance with robust multi-phase project execution capabilities."
        else:
            execution_rating = 7.0
            bias = "neutral"
            tier = "Regional Developer"
            summary = f"Execution risk profile for {developer} is within standard delivery parameters."

        evidence = [
            f"Developer classification: {tier} ({developer}).",
            f"Planned development volume: {units} residential units.",
            "Procurement and contractor management subject to milestone-linked escrow governance."
        ]

        metrics = {
            "developer": developer,
            "developer_tier": tier,
            "units_to_execute": units,
            "execution_readiness_score": execution_rating
        }

        limitations = [
            "Predictive construction schedule delay ML model is unavailable due to lack of contractor telemetry; evaluating execution capability based on developer governance tier."
        ]

        return AgentEvidence(
            agent_name=self.name,
            status="partial",
            decision_bias=bias,
            score=execution_rating,
            summary=summary,
            metrics=metrics,
            evidence=evidence,
            limitations=limitations,
            flags=[],
            tool_used="developer_track_record_assessment",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
