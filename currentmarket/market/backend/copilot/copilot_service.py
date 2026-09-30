import os
from typing import Dict, Any, List, Optional

from backend.copilot.llm_orchestrator import get_llm_orchestrator


class CopilotService:
    """
    Puravankara AI Decision Support Copilot Service.
    Strictly powered by pure LLM Orchestration and Evidence Synthesis.
    Zero deterministic fallback, zero regex intent routing, zero synthetic values.
    """

    def __init__(self):
        self.orchestrator = get_llm_orchestrator()

    def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Main chat handler. Routes questions through Stage-1 LLM Orchestration,
        executes approved intelligence tools on real database/ML/geospatial layers,
        and synthesizes answers via Stage-2 LLM synthesis.
        """
        return self.orchestrator.process_query(message, history or [])


_copilot_service: Optional[CopilotService] = None


def get_copilot_service() -> CopilotService:
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = CopilotService()
    return _copilot_service
