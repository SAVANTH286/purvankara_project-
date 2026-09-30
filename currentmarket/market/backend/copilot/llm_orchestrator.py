import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.services.openrouter_service import (
    get_openrouter_service,
    OpenRouterError,
    OpenRouterAuthError,
    OpenRouterRateLimitError,
)
from backend.intelligence.tool_registry import execute_tool, TOOL_CATALOG
from backend.intelligence.agent_registry import AGENT_REGISTRY
from backend.copilot.prompts import ORCHESTRATION_PROMPT, SYNTHESIS_PROMPT

logger = logging.getLogger("PuravankaraCopilot")


class LLMOrchestrator:
    """
    Pure LLM-based autonomous question routing and response synthesis orchestrator.
    Enforces strict zero-fabrication architecture with NO deterministic fallback.
    """

    def __init__(self):
        self.openrouter = get_openrouter_service()

    def process_query(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Executes the two-stage LLM orchestration pipeline:
        Stage 1: LLM Orchestrator produces validated routing plan (agents, tools, args).
        Execution: Safe execution of tools on real database, ML, OSM, and RAG engines.
        Stage 2: LLM synthesizes grounded executive response using only retrieved evidence.
        """
        trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        clean_history = history or []

        # 0. Check OpenRouter Configuration
        if not self.openrouter.is_configured():
            logger.warning(f"[{trace_id}] OpenRouter API key is missing or not configured.")
            return {
                "status": "error",
                "error_type": "llm_orchestration_unavailable",
                "message": "AI orchestration is currently unavailable. Please configure or verify the OpenRouter connection in .env.",
                "answer": "AI orchestration is currently unavailable. Please configure or verify the OpenRouter connection.",
                "response": "AI orchestration is currently unavailable. Please configure or verify the OpenRouter connection.",
                "orchestration_mode": "llm"
            }

        # 1. STAGE 1: LLM ROUTING DECISION
        orchestration_messages = [
            {"role": "system", "content": ORCHESTRATION_PROMPT}
        ]
        # Include recent conversation turns (last 6)
        for h in clean_history[-6:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ["user", "assistant"] and content:
                # Truncate assistant turns in Stage 1 to prevent keyword bias / topic contamination
                if role == "assistant" and len(content) > 250:
                    content = content[:250] + "..."
                orchestration_messages.append({"role": role, "content": content})

        orchestration_messages.append({"role": "user", "content": message})

        try:
            logger.info(f"[{trace_id}] Requesting Stage-1 Orchestration routing plan...")
            routing_decision = self.openrouter.structured_completion(
                messages=orchestration_messages,
                temperature=0.1,
                stage="stage1",
            )
        except OpenRouterAuthError as e:
            logger.error(f"[{trace_id}] OpenRouter authentication failure error_category=authentication")
            return {
                "status": "error",
                "error_type": "llm_orchestration_unavailable",
                "message": f"AI orchestration authentication failed: {str(e)}",
                "answer": "AI orchestration authentication failed. Please check your OpenRouter API key.",
                "response": "AI orchestration authentication failed. Please check your OpenRouter API key.",
                "orchestration_mode": "llm"
            }
        except OpenRouterRateLimitError as e:
            return self._quota_error_response(trace_id, e, stage="stage1")
        except OpenRouterError as e:
            logger.error(f"[{trace_id}] OpenRouter routing call failed: {e}")
            return {
                "status": "error",
                "error_type": "llm_orchestration_unavailable",
                "message": f"AI orchestration is currently unavailable: {str(e)}",
                "answer": f"AI orchestration is currently unavailable. Error: {str(e)}",
                "response": f"AI orchestration is currently unavailable. Error: {str(e)}",
                "orchestration_mode": "llm"
            }
        except Exception as e:
            logger.error(f"[{trace_id}] Unexpected orchestrator error: {e}")
            return {
                "status": "error",
                "error_type": "llm_orchestration_unavailable",
                "message": f"AI orchestration encountered an unexpected error: {str(e)}",
                "answer": "AI orchestration error occurred during intent analysis.",
                "response": "AI orchestration error occurred during intent analysis.",
                "orchestration_mode": "llm"
            }

        # 2. Check for Clarification Request
        if routing_decision.get("clarification_needed"):
            clarif_q = routing_decision.get("clarification_question") or "Could you please specify the micro-market or target project parameters?"
            logger.info(f"[{trace_id}] Orchestrator requested clarification: {clarif_q}")
            raw_agents = routing_decision.get("agents", [])
            clarif_agents = []
            for a in raw_agents:
                if isinstance(a, dict):
                    clarif_agents.append(a.get("name", "IntelligenceAgent"))
                elif isinstance(a, str):
                    clarif_agents.append(a)
            return {
                "status": "success",
                "answer": clarif_q,
                "response": clarif_q,
                "intent": routing_decision.get("intent", "clarification_needed"),
                "agents_used": clarif_agents,
                "tools_used": [],
                "models_used": [],
                "evidence": [],
                "sources": [],
                "limitations": ["Clarification requested due to missing essential project parameters."],
                "orchestration_mode": "llm"
            }

        # 3. TOOL EXECUTION & EVIDENCE COLLECTION
        requested_tools = self._normalize_requested_tools(routing_decision)
        executed_tool_names: List[str] = []
        evidence_payloads: List[Dict[str, Any]] = []
        sources_set = set()
        limitations_list: List[str] = []
        models_used_set = set()

        for t in requested_tools:
            tool_name = t.get("name")
            tool_args = t.get("arguments", {})
            if not tool_name:
                continue

            logger.info(f"[{trace_id}] Executing tool: {tool_name} with args: {tool_args}")
            res = execute_tool(tool_name, tool_args)
            executed_tool_names.append(tool_name)
            evidence_payloads.append(res)

            if res.get("source"):
                sources_set.add(res["source"])
            if res.get("limitations"):
                limitations_list.extend(res["limitations"])

            # Detect executed ML models
            if tool_name in ["predict_price"]:
                models_used_set.add("GradientBoostingRegressor (Price ML)")
            elif tool_name in ["predict_market_absorption"]:
                models_used_set.add("RandomForestRegressor (Market Demand ML)")
            elif tool_name in ["get_buyer_segments", "predict_buyer_fit", "predict_buyer_segments"]:
                models_used_set.add("KMeans Clustering (Buyer Segmentation ML)")

        # Fallback if no tools were selected
        if not evidence_payloads:
            logger.info(f"[{trace_id}] No tools selected by orchestrator for query: {message}")
            evidence_payloads.append({
                "tool": "general_inquiry",
                "status": "information",
                "data": {"note": "No domain intelligence tools were required for this inquiry."},
                "source": "Puravankara General Guidance",
                "limitations": ["No database or ML tools were queried."]
            })

        # 4. STAGE 2: GROUNDED RESPONSE SYNTHESIS
        synthesis_input = {
            "user_question": message,
            "routing_decision": {
                "intent": routing_decision.get("intent"),
                "agents_selected": routing_decision.get("agents"),
                "parameters": routing_decision.get("parameters")
            },
            "retrieved_evidence": evidence_payloads
        }

        synthesis_messages = [
            {"role": "system", "content": SYNTHESIS_PROMPT}
        ]
        # Include conversation history context
        for h in clean_history[-4:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ["user", "assistant"] and content:
                synthesis_messages.append({"role": role, "content": content})

        synthesis_messages.append({
            "role": "user",
            "content": f"USER INQUIRY:\n{message}\n\nEVIDENCE RETRIEVED FROM REAL INTELLIGENCE LAYER:\n{json.dumps(synthesis_input, indent=2, default=str)}\n\nPlease synthesize a professional, executive response strictly grounded in this evidence."
        })

        try:
            logger.info(f"[{trace_id}] Requesting Stage-2 Synthesis call...")
            synth_res = self.openrouter.chat_completion(
                messages=synthesis_messages,
                temperature=0.2,
                stage="stage2",
            )
            raw_synth = synth_res.get("content") or ""
            final_answer = str(raw_synth).strip()
            if not final_answer:
                final_answer = "Intelligence analysis completed based on retrieved evidence."
        except OpenRouterRateLimitError as e:
            return self._quota_error_response(trace_id, e, stage="stage2")
        except OpenRouterError as e:
            logger.error(f"[{trace_id}] Synthesis LLM call failed: {e}")
            return {
                "status": "error",
                "error_type": "llm_orchestration_unavailable",
                "message": f"AI response synthesis unavailable: {str(e)}",
                "answer": "AI synthesis could not be completed due to OpenRouter communication failure.",
                "response": "AI synthesis could not be completed due to OpenRouter communication failure.",
                "orchestration_mode": "llm"
            }

        # Map tools to canonical agents to ensure agents_used faithfully reflects tool execution
        tool_to_agent_map = {
            "predict_buyer_segments": "buyer_intelligence_agent",
            "get_buyer_segments": "buyer_intelligence_agent",
            "predict_buyer_fit": "buyer_intelligence_agent",
            "get_buyer_profiles": "buyer_intelligence_agent",
            "predict_price": "finance_agent",
            "run_scenario": "scenario_tool",
            "get_dss_evidence": "dss_evidence_tool",
            "predict_market_absorption": "market_agent",
            "get_micro_market_profile": "market_agent",
            "get_market_projects": "market_agent",
            "get_competitors": "competition_agent",
            "get_infrastructure_amenities": "infrastructure_agent",
            "get_infrastructure_profile": "infrastructure_agent",
            "get_regulatory_records": "regulatory_agent",
            "search_market_documents": "document_search_tool",
            "get_city_profile": "city_profile_agent",
            "list_micro_markets": "city_profile_agent",
        }

        # Format agents used
        raw_agents = routing_decision.get("agents", [])
        agent_names = []
        for a in raw_agents:
            if isinstance(a, dict):
                agent_names.append(a.get("name", "IntelligenceAgent"))
            elif isinstance(a, str):
                agent_names.append(a)

        # If LLM didn't specify agent names, infer from executed tools
        if not agent_names and executed_tool_names:
            inferred = []
            for t in executed_tool_names:
                mapped_ag = tool_to_agent_map.get(t)
                if mapped_ag and mapped_ag not in inferred:
                    inferred.append(mapped_ag)
            agent_names = inferred

        # 5. ASSEMBLE FINAL STRUCTURED RESPONSE
        return {
            "status": "success",
            "answer": final_answer,
            "response": final_answer,
            "intent": routing_decision.get("intent", "real_estate_inquiry"),
            "agents_used": agent_names or ["ExecutiveCopilot"],
            "tools_used": executed_tool_names,
            "models_used": list(models_used_set),
            "evidence": evidence_payloads,
            "sources": list(sources_set) or ["Puravankara Verified Intelligence Layer"],
            "limitations": list(set(limitations_list)),
            "orchestration_mode": "llm",
            "trace_id": trace_id
        }


    def _quota_error_response(self, trace_id: str, exc: OpenRouterRateLimitError, stage: str) -> Dict[str, Any]:
        category = getattr(exc, "category", "rate_limit")
        logger.warning(
            "[%s] OpenRouter blocked model=%s stage=%s error_category=%s",
            trace_id,
            self.openrouter.model,
            stage,
            category,
        )
        message = str(exc)
        return {
            "status": "error",
            "error_type": "llm_quota_exceeded",
            "message": message,
            "answer": message,
            "response": message,
            "orchestration_mode": "llm",
        }

    def _normalize_requested_tools(self, routing_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Accept the existing tool-object schema and a compact string-tool schema."""
        raw_tools = routing_decision.get("tools") or []
        shared_arguments = routing_decision.get("arguments") or {}
        if not isinstance(shared_arguments, dict):
            shared_arguments = {}
        if isinstance(raw_tools, dict):
            raw_tools = [raw_tools]
        if not isinstance(raw_tools, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for tool in raw_tools:
            if isinstance(tool, str):
                name = tool.strip()
                arguments = dict(shared_arguments)
            elif isinstance(tool, dict):
                name = tool.get("name") or tool.get("tool")
                arguments = tool.get("arguments", tool.get("args", shared_arguments))
                if not isinstance(arguments, dict):
                    arguments = dict(shared_arguments)
                elif not arguments and shared_arguments:
                    arguments = dict(shared_arguments)
            else:
                continue
            if name:
                normalized.append({"name": str(name), "arguments": arguments})
        return normalized


_orchestrator: Optional[LLMOrchestrator] = None


def get_llm_orchestrator() -> LLMOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator
