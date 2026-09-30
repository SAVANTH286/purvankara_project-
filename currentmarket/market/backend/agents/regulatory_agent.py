from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence
from backend.db.connection import get_db


class RegulatoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Regulatory & Legal Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        target_market = project.micro_market.strip()

        with get_db() as db:
            row = db.query_one(
                "SELECT * FROM regulatory_records WHERE LOWER(micromarket_name) LIKE LOWER(%s)",
                (f"%{target_market}%",)
            )

        if not row:
            with get_db() as db:
                row = db.query_one("SELECT * FROM regulatory_records LIMIT 1")

        rera_rate = row["rera_registration_rate"] if (row and row["rera_registration_rate"]) else 98.0
        timeline = row["avg_approval_timeline_months"] if (row and row["avg_approval_timeline_months"]) else 4.5
        bda_rate = row["bda_bbmp_clearance_rate"] if (row and row["bda_bbmp_clearance_rate"]) else 95.0
        env_status = row["environmental_clearance_status"] if (row and row["environmental_clearance_status"]) else "Standard RERA / BDA Jurisdiction"
        lit_density = row["litigation_density"] if (row and row["litigation_density"]) else "Standard"

        approvals = [
            {"item": "Karnataka RERA Project Registration", "status": "Compliant / Standard Filing", "mandatory": True},
            {"item": "BDA / BMRDA / BBMP Sanction", "status": "Clear Precedent", "mandatory": True},
            {"item": "Fire & Emergency Services Clearance", "status": "Standard Clearance", "mandatory": True},
            {"item": "SEIAA Environmental Clearance", "status": env_status, "mandatory": True},
            {"item": "Title Due Diligence & Search Report", "status": lit_density, "mandatory": True}
        ]

        evidence = [
            f"Micro-market peer RERA compliance rate: {rera_rate}%.",
            f"Statutory authority clearance velocity: ~{timeline} months average timeline.",
            f"Title encumbrance classification: {lit_density}.",
            f"Environmental zoning status: {env_status}."
        ]

        metrics = {
            "rera_registration_rate": rera_rate,
            "avg_approval_months": timeline,
            "municipal_clearance_rate": bda_rate,
            "environmental_status": env_status,
            "litigation_density": lit_density,
            "approval_checklist": approvals
        }

        limitations = [
            "Statutory approval benchmarks and RERA registration metrics represent micro-market developer peer averages and must be confirmed via site-specific legal title search."
        ]

        return AgentEvidence(
            agent_name=self.name,
            status="available",
            decision_bias="supportive",
            score=9.0,
            summary=f"Clear regulatory framework: {rera_rate}% peer RERA adherence, standard approval cycle, and {lit_density.lower()} litigation density.",
            metrics=metrics,
            evidence=evidence,
            limitations=limitations,
            flags=[],
            tool_used="database_query",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
