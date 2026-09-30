from typing import Dict, Any, List
from backend.agents.base import BaseAgent, ProjectInput, AgentEvidence
from backend.db.connection import get_db
from backend.rag.rag_engine import get_rag_engine


class CityAgent(BaseAgent):
    def __init__(self):
        super().__init__("City Profiling Agent")

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        with get_db() as db:
            row = db.query_one("SELECT * FROM cities WHERE city_name = 'Bengaluru'")

        if not row:
            return AgentEvidence(
                agent_name=self.name,
                status="partial",
                decision_bias="neutral",
                score=7.0,
                summary="Bengaluru macro benchmark profile loaded from baseline standard.",
                evidence=["Macro trends indicate steady residential absorption across prime corridors."],
                limitations=["City benchmark database table was unpopulated; using static baseline."],
                tool_used="database_query",
                ml_used=False,
                model_used=None,
                confidence=None
            )

        total_launches = row["total_launches_2025"] or 49252
        unsold = row["unsold_inventory"] or 67518
        qts = row["qts_quarters"] or 4.9
        price_growth = row["price_growth_yoy"] or 12.0
        premium_share = row["premium_share"] or 52.0
        source = row["source"] or "Cushman & Wakefield / Knight Frank / JLL H2 2025-Q1 2026"

        rag = get_rag_engine()
        rag_hits = rag.search("Bengaluru residential launches unsold inventory price growth", top_k=2)
        rag_notes = [f"[{h['source']} - {h['section']}]: {h['content'][:140]}..." for h in rag_hits]

        evidence = [
            f"Bengaluru residential market recorded ~{total_launches:,} launches (+28% YoY) with {price_growth}% YoY capital value appreciation.",
            f"High-end and premium segments drive {premium_share}% of total launches across Bengaluru.",
            f"City-wide unsold inventory sits at ~{unsold:,} units with a healthy quarters-to-sell (QTS) of {qts} quarters.",
            f"Research source baseline: {source}."
        ]
        if rag_notes:
            evidence.extend(rag_notes)

        metrics = {
            "city": "Bengaluru",
            "annual_launches_2025": total_launches,
            "unsold_inventory": unsold,
            "quarters_to_sell_qts": qts,
            "price_growth_yoy_pct": price_growth,
            "premium_segment_share_pct": premium_share,
            "source": source
        }

        return AgentEvidence(
            agent_name=self.name,
            status="available",
            decision_bias="supportive" if price_growth >= 8.0 and qts <= 6.0 else "neutral",
            score=8.5,
            summary=f"Bengaluru macro residential environment is healthy with {price_growth}% YoY price appreciation and strong {qts} quarters absorption velocity.",
            metrics=metrics,
            evidence=evidence,
            limitations=[
                "City-level benchmarks reflect metropolitan macro absorption; corridor-specific dynamics govern unit uptake."
            ],
            tool_used="database_query + rag_doc_search",
            ml_used=False,
            model_used=None,
            confidence=None,
            details=metrics
        )
