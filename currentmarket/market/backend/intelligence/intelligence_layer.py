from typing import Dict, Any, List
from backend.intelligence.orchestrator import get_orchestrator, DSSOrchestrator
from backend.intelligence.tool_registry import (
    get_city_profile,
    list_micro_markets,
    get_micro_market_profile,
    get_market_projects,
    get_competitors,
    get_buyer_profiles,
    get_buyer_segments,
    get_regulatory_records,
    get_infrastructure_profile,
    search_market_documents
)


class IntelligenceLayer:
    """
    Unified Intelligence Layer for both DSS and AI Copilot.
    Provides structured data access, ML inference, and full project evaluation.
    """

    @staticmethod
    def evaluate_project(project_data: dict) -> Dict[str, Any]:
        from backend.agents.base import ProjectInput
        project = ProjectInput(**project_data)
        orchestrator = get_orchestrator()
        return orchestrator.evaluate_project(project)

    @staticmethod
    def get_tool_catalog() -> List[Dict[str, Any]]:
        from backend.intelligence.tool_registry import TOOL_CATALOG
        return TOOL_CATALOG
