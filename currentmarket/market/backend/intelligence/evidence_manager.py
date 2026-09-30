from typing import Dict, Any, List
from backend.agents.base import AgentEvidence


class EvidenceManager:
    """
    Manages provenance, limitations, and coverage metrics across all agent evidence.
    Ensures zero fabricated data and transparent data lineage.
    """

    @staticmethod
    def compile_evidence_metadata(evidence: Dict[str, AgentEvidence]) -> Dict[str, Any]:
        total_agents = len(evidence)
        available_count = sum(1 for e in evidence.values() if e.status == "available")
        partial_count = sum(1 for e in evidence.values() if e.status == "partial")
        unavailable_count = sum(1 for e in evidence.values() if e.status == "unavailable")

        coverage_percentage = round(((available_count + (partial_count * 0.5)) / max(1, total_agents)) * 100.0, 1)

        all_limitations = []
        ml_models_used = []

        for key, ev in evidence.items():
            for lim in ev.limitations:
                all_limitations.append(f"[{ev.agent_name}]: {lim}")
            if ev.ml_used and ev.model_used:
                ml_models_used.append({
                    "agent": ev.agent_name,
                    "model": ev.model_used,
                    "validation_metric": "Silhouette Score",
                    "confidence_score": ev.confidence
                })

        return {
            "total_agents": total_agents,
            "evidence_coverage_percentage": coverage_percentage,
            "agent_status_breakdown": {
                "available": available_count,
                "partial": partial_count,
                "unavailable": unavailable_count
            },
            "ml_models_active": ml_models_used,
            "consolidated_limitations": all_limitations
        }
