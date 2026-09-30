from typing import List, Dict, Any
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence
from backend.db.connection import get_db


class CompetitionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Competition Intelligence Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        target_market = project.micro_market.strip()
        segment = project.property_segment.strip()
        requested_bhk = project.bhk or "3BHK"

        with get_db() as db:
            rows = db.query(
                """
                SELECT * FROM projects 
                WHERE LOWER(micromarket_name) LIKE LOWER(%s)
                ORDER BY id ASC
                """,
                (f"%{target_market}%",)
            )

        # Convert rows to dicts for safe dictionary access
        dict_rows = [dict(r) for r in rows] if rows else []

        # Filter comparable projects by segment if available
        comparables = [r for r in dict_rows if str(r.get("property_segment", "")).lower() == segment.lower()]
        if not comparables and dict_rows:
            comparables = dict_rows

        # Factual count based on real projects in DB
        comparable_count = len(comparables)

        # Check known BHK data
        known_bhk_count = sum(1 for r in comparables if r.get("bhk_configurations"))
        bhk_coverage_status = "sufficient" if known_bhk_count > 0 else "insufficient"

        evidence = []
        if comparable_count > 0:
            evidence.append(
                f"{comparable_count} historical comparable projects were identified for the supplied "
                f"property type and segment within the selected micro-market."
            )
        else:
            evidence.append(
                "No historical comparable projects were identified using the supplied property type and segment."
            )

        if bhk_coverage_status == "insufficient":
            evidence.append(
                f"BHK-specific comparison for {requested_bhk} is unavailable because the comparable "
                "projects do not contain sufficient known BHK data."
            )

        evidence.append("Comparable-project price evidence is insufficient for a price comparison.")

        flags = []
        if comparable_count >= 20:
            bias = "caution"
            score = 6.0
            flags.append(f"High competitive supply density ({comparable_count} projects).")
        else:
            bias = "supportive"
            score = 8.0

        sample_comps = []
        if comparables:
            for r in comparables[:8]:
                sample_comps.append({
                    "project_name": r.get("project_name"),
                    "developer": r.get("developer"),
                    "price_per_sqft": r.get("price_per_sqft"),
                    "units": r.get("launched_units"),
                    "percentage_sold": r.get("percentage_sold")
                })

        metrics = {
            "comparable_project_count": comparable_count,
            "bhk_coverage_status": bhk_coverage_status,
            "known_bhk_count": known_bhk_count,
            "competitors_sample": sample_comps
        }

        limitations = [
            "BHK configuration granularity in historical competitive projects is unrecorded in current survey, precluding unit-level BHK pricing variance modeling."
        ]

        return AgentEvidence(
            agent_name=self.name,
            status="partial",
            decision_bias=bias,
            score=score,
            summary=f"Identified {comparable_count} historical comparable projects in {target_market}; active peer presence.",
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
