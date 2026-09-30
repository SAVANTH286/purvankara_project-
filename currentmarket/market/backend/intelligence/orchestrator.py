from typing import Dict, Any, List
from backend.agents import (
    ProjectInput,
    AgentEvidence,
    CityAgent,
    LocationAgent,
    MarketAgent,
    CompetitionAgent,
    InfrastructureAgent,
    BuyerAgent,
    FinanceAgent,
    RegulatoryAgent,
    ExecutionAgent,
    PortfolioAgent
)
from backend.engine import RiskEngine, DecisionEngine
from backend.intelligence.evidence_manager import EvidenceManager
from ml.market.infer import predict_market_absorption
from ml.price.infer import predict_price_per_sqft
from ml.buyer.infer import evaluate_buyer_fit
from backend.services.geospatial_service import resolve_coordinates
from backend.services.amenity_service import get_amenity_service


class DSSOrchestrator:
    def __init__(self):
        self.agents = {
            "city": CityAgent(),
            "location": LocationAgent(),
            "market": MarketAgent(),
            "competition": CompetitionAgent(),
            "infrastructure": InfrastructureAgent(),
            "buyer": BuyerAgent(),
            "finance": FinanceAgent(),
            "regulatory": RegulatoryAgent(),
            "execution": ExecutionAgent(),
            "portfolio": PortfolioAgent()
        }
        self.risk_engine = RiskEngine()
        self.decision_engine = DecisionEngine()

    def evaluate_project(self, project: ProjectInput) -> Dict[str, Any]:
        """
        Executes all 10 specialized intelligence agents, compiles evidence,
        runs ML predictions, queries geospatial amenities, runs risk and
        decision engines, and formats the consolidated audit.
        """
        # 1. Run all 10 agents
        evidence_map: Dict[str, AgentEvidence] = {}
        for key, agent in self.agents.items():
            try:
                evidence_map[key] = agent.evaluate(project)
            except Exception as e:
                # Resilient fallback if an individual agent hits an unexpected error
                evidence_map[key] = AgentEvidence(
                    agent_name=agent.name,
                    status="unavailable",
                    decision_bias="neutral",
                    score=5.0,
                    summary=f"Evaluation encountered an issue: {str(e)}",
                    limitations=[str(e)],
                    tool_used="error_handler",
                    ml_used=False,
                    confidence=None
                )

        # 2. Execute Real ML Predictions for this Project
        market_ml = predict_market_absorption(
            micromarket_name=project.micro_market,
            units=project.units,
            price_per_sqft=project.price_per_sqft
        )
        price_ml = predict_price_per_sqft(
            micromarket_name=project.micro_market,
            property_segment=project.property_segment,
            property_type=project.property_type,
            bhk_str=project.bhk or "3BHK",
            units=project.units
        )
        buyer_ml = evaluate_buyer_fit(
            bhk_str=project.bhk or "3BHK",
            property_segment=project.property_segment,
            price_per_sqft=project.price_per_sqft
        )

        ml_predictions = {
            "market_demand": market_ml,
            "price_prediction": price_ml,
            "buyer_fit": buyer_ml
        }

        # 3. Resolve Project Coordinates & Geospatial 5km Amenities
        if project.latitude is not None and project.longitude is not None:
            lat, lon = float(project.latitude), float(project.longitude)
        else:
            lat, lon = resolve_coordinates(project.micro_market, project.location)
        amenity_svc = get_amenity_service()
        geo_result = amenity_svc.get_amenities_within_radius(lat, lon, radius_km=5.0)

        # 4. Risk Engine Evaluation
        risk_profile = self.risk_engine.evaluate(project, evidence_map)

        # 5. Decision Engine Synthesis
        decision_result = self.decision_engine.evaluate(project, evidence_map, risk_profile)

        # 5b. Attach Price Intelligence observation if coverage is limited or baseline
        price_cov = price_ml.get("coverage_status")
        price_warn = price_ml.get("warning")
        if price_warn and "observations" in decision_result:
            decision_result["observations"].append(f"Price Intelligence [{price_cov}]: {price_warn}")

        # 6. Evidence Metadata (coverage, limitations, ML lineage)
        evidence_meta = EvidenceManager.compile_evidence_metadata(evidence_map)

        # 7. Serialize evidence for API response
        serialized_evidence = {k: v.model_dump() for k, v in evidence_map.items()}

        price_evidence = {
            "prediction": price_ml.get("predicted_price_per_sqft"),
            "coverage_status": price_ml.get("coverage_status"),
            "observations": price_ml.get("market_observation_count", 0),
            "developments": price_ml.get("market_development_count", 0),
            "developers": price_ml.get("market_developer_count", 0),
            "model_version": price_ml.get("model_version"),
            "confidence_status": price_ml.get("confidence_status"),
            "warning": price_ml.get("warning")
        }

        return {
            "project_name": project.project_name,
            "developer": project.developer,
            "location": project.location,
            "micro_market": project.micro_market,
            "property_segment": project.property_segment,
            "property_type": project.property_type,
            "bhk": project.bhk,
            "units": project.units,
            "price_per_sqft": project.price_per_sqft,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "decision": decision_result["decision"],
            "decision_is_provisional": decision_result["decision_is_provisional"],
            "provisional_reasons": decision_result["provisional_reasons"],
            "confidence": decision_result["confidence"],  # strictly null unless validated by ML
            "executive_summary": decision_result["executive_summary"],
            "positive_drivers": decision_result["positive_drivers"],
            "cautionary_flags": decision_result["cautionary_flags"],
            "recommended_actions": decision_result["recommended_actions"],
            "observations": decision_result["observations"],
            "risk_assessment": risk_profile,
            "evidence_coverage": evidence_meta["evidence_coverage_percentage"],
            "evidence_metadata": evidence_meta,
            "ml_predictions": ml_predictions,
            "price_evidence": price_evidence,
            "geospatial": geo_result,
            "evidence": serialized_evidence
        }


# Global instance
_orchestrator = None


def get_orchestrator() -> DSSOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DSSOrchestrator()
    return _orchestrator
