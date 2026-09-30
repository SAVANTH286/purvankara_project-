import pytest
from unittest.mock import patch, MagicMock
from backend.services.openrouter_service import (
    OpenRouterService,
    OpenRouterAuthError,
    OpenRouterError,
    OpenRouterJSONError,
    OpenRouterRateLimitError,
)
from backend.intelligence.tool_registry import execute_tool, TOOL_CATALOG
from backend.intelligence.agent_registry import list_registered_agents, AGENT_REGISTRY
from backend.copilot.llm_orchestrator import LLMOrchestrator, get_llm_orchestrator
from backend.copilot.copilot_service import CopilotService, get_copilot_service


# -----------------------------------------------------------------------------
# 1. TEST: TOOL EXECUTION & DATA INTEGRITY
# -----------------------------------------------------------------------------

def test_tool_catalog_contains_expected_tools():
    tool_names = [t["name"] for t in TOOL_CATALOG]
    expected = [
        "get_city_profile",
        "list_micro_markets",
        "get_micro_market_profile",
        "get_market_projects",
        "get_competitors",
        "get_buyer_profiles",
        "get_buyer_segments",
        "predict_market_absorption",
        "predict_price",
        "get_infrastructure_amenities",
        "get_infrastructure_profile",
        "get_regulatory_records",
        "search_market_documents",
        "get_dss_evidence",
        "run_scenario"
    ]
    for exp in expected:
        assert exp in tool_names, f"Missing tool: {exp}"


def test_agent_registry_contains_all_agents():
    agents = list_registered_agents()
    agent_names = [a["name"] for a in agents]
    expected_agents = [
        "city_profile_agent",
        "location_agent",
        "market_agent",
        "competition_agent",
        "infrastructure_agent",
        "buyer_intelligence_agent",
        "finance_agent",
        "regulatory_agent",
        "project_execution_agent",
        "portfolio_agent",
        "dss_evidence_tool",
        "scenario_tool",
        "document_search_tool"
    ]
    for exp in expected_agents:
        assert exp in agent_names, f"Missing agent: {exp}"


def test_tool_execution_market_profile():
    res = execute_tool("get_micro_market_profile", {"market_name": "Kanakapura Road"})
    assert res["status"] == "success"
    assert res["data"]["micromarket_name"] == "Kanakapura Road"
    assert "average_percentage_sold" in res["data"]
    assert "source" in res
    assert "limitations" in res


def test_tool_execution_market_projects():
    res = execute_tool("get_market_projects", {"market_name": "Kanakapura Road"})
    assert res["status"] == "success"
    assert "projects" in res["data"]
    assert len(res["data"]["projects"]) > 0


def test_tool_execution_competitors():
    res = execute_tool("get_competitors", {"market_name": "Kanakapura Road"})
    assert res["status"] == "success"
    assert "competitors" in res["data"]


def test_tool_execution_buyer_profiles():
    res = execute_tool("get_buyer_profiles", {})
    assert res["status"] == "success"
    assert res["data"]["sample_size"] == 2583


def test_tool_execution_buyer_segments():
    res = execute_tool("get_buyer_segments", {"bhk_str": "3BHK", "property_segment": "Mid", "price_per_sqft": 6500.0})
    assert res["status"] == "success"
    assert "primary_segment" in res["data"]


def test_tool_execution_predict_buyer_segments():
    res = execute_tool("predict_buyer_segments", {"bhk_str": "3BHK", "property_segment": "Mid", "price_per_sqft": 6500.0})
    assert res["status"] == "success"
    assert "primary_segment" in res["data"]
    assert "buyer_fit_index" in res["data"]
    assert isinstance(res["data"]["primary_segment"], str)


def test_tool_execution_predict_absorption():
    res = execute_tool("predict_market_absorption", {"micromarket_name": "Kanakapura Road", "units": 300, "price_per_sqft": 6500.0})
    assert res["status"] == "success"
    assert "predicted_absorption_pct" in res["data"]


def test_tool_execution_predict_price():
    res = execute_tool("predict_price", {"micromarket_name": "Kanakapura Road", "property_segment": "Mid", "bhk_str": "3BHK", "units": 300})
    assert res["status"] == "success"
    assert "predicted_price_per_sqft" in res["data"]


def test_tool_execution_infrastructure_amenities():
    res = execute_tool("get_infrastructure_amenities", {"market_name": "Kanakapura Road", "radius_km": 5.0})
    assert res["status"] == "success"
    assert "total_count" in res["data"]


def test_tool_execution_search_market_documents():
    res = execute_tool("search_market_documents", {"query": "Bengaluru demand"})
    assert res["status"] == "success"
    assert "excerpts" in res["data"]


def test_tool_execution_dss_evidence():
    res = execute_tool("get_dss_evidence", {"micro_market": "Kanakapura Road", "units": 300, "price_per_sqft": 6500.0, "bhk": "3BHK"})
    assert res["status"] == "success"
    assert "decision" in res["data"]
    assert res["data"]["decision"] in ["Launch", "Hold", "No-Launch"]


def test_tool_execution_run_scenario():
    res = execute_tool("run_scenario", {
        "micro_market": "Kanakapura Road",
        "base_price_per_sqft": 6500.0,
        "base_units": 300,
        "base_bhk": "3BHK",
        "new_price_per_sqft": 8050.0,
        "new_units": 440,
        "new_bhk": "4BHK"
    })
    assert res["status"] == "success"
    assert "deltas" in res["data"]
    assert "scenario_verdict" in res["data"]


def test_tool_security_blocks_unauthorized_tools():
    res = execute_tool("system_exec_rm_rf", {"cmd": "rm -rf /"})
    assert res["status"] == "error"
    assert "not registered" in res["error"]


# -----------------------------------------------------------------------------
# 2. TEST: UNCONFIGURED OPENROUTER RETURNS EXPLICIT ERROR (NO FALLBACK)
# -----------------------------------------------------------------------------

def test_unconfigured_openrouter_returns_error_and_no_deterministic_fallback():
    orchestrator = LLMOrchestrator()
    # Temporarily ensure API key is empty
    with patch.object(orchestrator.openrouter, "is_configured", return_value=False):
        res = orchestrator.process_query("What is the absorption in Kanakapura Road?")
        assert res["status"] == "error"
        assert res["error_type"] == "llm_orchestration_unavailable"
        assert "AI orchestration is currently unavailable" in res["message"]
        # Must NOT be deterministic fallback
        assert res.get("orchestration_mode") == "llm"


# -----------------------------------------------------------------------------
# 3. TEST: TWO-STAGE ORCHESTRATION WITH MOCKED LLM
# -----------------------------------------------------------------------------

def test_two_stage_orchestration_multi_agent_multi_tool():
    orchestrator = LLMOrchestrator()

    mock_routing_decision = {
        "intent": "micro_market_comparison",
        "agents": [
            {"name": "market_agent", "reason": "Analyze market absorption in both corridors."},
            {"name": "competition_agent", "reason": "Check competitor projects in both corridors."},
            {"name": "buyer_intelligence_agent", "reason": "Evaluate buyer demographic fit."}
        ],
        "tools": [
            {"name": "get_micro_market_profile", "arguments": {"market_name": "Kanakapura Road"}},
            {"name": "get_micro_market_profile", "arguments": {"market_name": "Bagalur"}},
            {"name": "get_competitors", "arguments": {"market_name": "Kanakapura Road"}},
            {"name": "get_buyer_segments", "arguments": {"bhk_str": "3BHK", "property_segment": "Mid", "price_per_sqft": 7000.0}}
        ],
        "parameters": {
            "micro_markets": ["Kanakapura Road", "Bagalur"],
            "bhk": "3BHK",
            "price_per_sqft": 7000.0
        },
        "clarification_needed": False,
        "clarification_question": None
    }

    mock_synthesis_response = {
        "content": "### Comparative Analysis: Kanakapura Road vs Bagalur\n\nKanakapura Road demonstrates 95.69% absorption, while Bagalur displays strong momentum...",
        "raw": {},
        "model_used": "google/gemini-2.5-flash"
    }

    with patch.object(orchestrator.openrouter, "is_configured", return_value=True), \
         patch.object(orchestrator.openrouter, "structured_completion", return_value=mock_routing_decision), \
         patch.object(orchestrator.openrouter, "chat_completion", return_value=mock_synthesis_response):

        res = orchestrator.process_query("Compare Kanakapura Road and Bagalur for a 3BHK launch considering market demand, competition and buyer fit.")

        assert res["status"] == "success"
        assert res["intent"] == "micro_market_comparison"
        assert "market_agent" in res["agents_used"]
        assert "competition_agent" in res["agents_used"]
        assert "buyer_intelligence_agent" in res["agents_used"]
        assert len(res["tools_used"]) == 4
        assert len(res["evidence"]) == 4
        assert "KMeans Clustering (Buyer Segmentation ML)" in res["models_used"]
        assert res["orchestration_mode"] == "llm"
        assert "Kanakapura Road" in res["answer"]


def test_buyer_intelligence_routing_and_model_detection():
    orchestrator = LLMOrchestrator()

    mock_routing_decision = {
        "intent": "BUYER_INTELLIGENCE",
        "agents": ["buyer_intelligence_agent"],
        "tools": [
            {"name": "predict_buyer_segments", "arguments": {"bhk_str": "3BHK", "property_segment": "Mid", "price_per_sqft": 6500.0, "units": 300}}
        ],
        "parameters": {
            "bhk": "3BHK",
            "property_segment": "Mid"
        },
        "clarification_needed": False,
        "clarification_question": None
    }

    mock_synthesis_response = {
        "content": "### Historical 3BHK Buyer Demographics\n\nBased on 2,583 verified Puravankara customer bookings...",
        "raw": {},
        "model_used": "qwen/qwen-2.5-7b-instruct:free"
    }

    with patch.object(orchestrator.openrouter, "is_configured", return_value=True), \
         patch.object(orchestrator.openrouter, "structured_completion", return_value=mock_routing_decision), \
         patch.object(orchestrator.openrouter, "chat_completion", return_value=mock_synthesis_response):

        res = orchestrator.process_query("Historical buyer demographics for 3BHK")

        assert res["status"] == "success"
        assert res["intent"] == "BUYER_INTELLIGENCE"
        assert "buyer_intelligence_agent" in res["agents_used"]
        assert "predict_buyer_segments" in res["tools_used"]
        assert "KMeans Clustering (Buyer Segmentation ML)" in res["models_used"]
        assert len(res["evidence"]) == 1
        assert "3BHK" in res["answer"]



def test_clarification_flow_when_essential_parameters_missing():
    orchestrator = LLMOrchestrator()

    mock_routing_decision = {
        "intent": "price_evaluation",
        "agents": [],
        "tools": [],
        "parameters": {},
        "clarification_needed": True,
        "clarification_question": "Which micro-market and property segment would you like me to evaluate?"
    }

    with patch.object(orchestrator.openrouter, "is_configured", return_value=True), \
         patch.object(orchestrator.openrouter, "structured_completion", return_value=mock_routing_decision):

        res = orchestrator.process_query("What price should we launch at?")

        assert res["status"] == "success"
        assert res["intent"] == "price_evaluation"
        assert "Which micro-market and property segment" in res["answer"]
        assert len(res["tools_used"]) == 0


def test_structured_completion_extracts_json_with_preamble_and_thoughts():
    svc = OpenRouterService()
    
    # Simulate LLM outputting reasoning preamble before emitting the JSON object
    noisy_output = {
        "content": (
            "We need need output strict JSON orchestrator only. User asks run scenario specific args. "
            "Need select scenario_tool likely only. Need understand Blind Spot revenue loss if no action.\n"
            "{\n"
            '  "intent": "run_blind_spot_scenario",\n'
            '  "agents": ["scenario_tool", "finance_agent"],\n'
            '  "tools": [{"name": "run_scenario", "arguments": {"micro_market": "Kanakapura Road", "base_price_per_sqft": 6500, "base_units": 300, "competitor_launch_month": 4}}],\n'
            '  "parameters": {"micro_market": "Kanakapura Road", "price_per_sqft": 6500, "units": 300},\n'
            '  "clarification_needed": false,\n'
            '  "clarification_question": null\n'
            "}\n"
            "This completes the JSON output."
        ),
        "raw": {},
        "model_used": "qwen/qwen-2.5-7b-instruct:free"
    }

    with patch.object(svc, "chat_completion", return_value=noisy_output):
        res = svc.structured_completion([{"role": "user", "content": "test"}])
        assert isinstance(res, dict)
        assert res["intent"] == "run_blind_spot_scenario"
        assert "scenario_tool" in res["agents"]
        assert len(res["tools"]) == 1
        assert res["tools"][0]["name"] == "run_scenario"
        assert res["tools"][0]["arguments"]["micro_market"] == "Kanakapura Road"


def _completion_response(content, model):
    resp = MagicMock()
    resp.status_code = 200
    resp.headers = {}
    resp.json.return_value = {
        "model": model,
        "choices": [{"message": {"role": "assistant", "content": content}}],
    }
    return resp


def test_safety_classifier_route_is_retried_on_the_same_free_model():
    svc = OpenRouterService()
    svc.model = "openrouter/free"
    safety = _completion_response("User Safety: safe", "nvidia/nemotron-3.5-content-safety:free")
    answer = _completion_response(
        '{"intent":"CITY_OVERVIEW","agents":["city_profile_agent"],"tools":[{"name":"get_city_profile","arguments":{}}],"clarification_needed":false}',
        "liquid/lfm-2.5-2.6b:free",
    )

    with patch.object(svc, "_refresh_config"), \
         patch.object(svc, "is_configured", return_value=True), \
         patch.object(svc.session, "post", side_effect=[safety, answer]) as post_mock:
        svc.api_key = "configured-test-key"
        res = svc.structured_completion([{"role": "user", "content": "overview"}], stage="stage1")

    assert post_mock.call_count == 2
    assert post_mock.call_args_list[0].kwargs["json"]["model"] == "openrouter/free"
    assert post_mock.call_args_list[1].kwargs["json"]["model"] == "openrouter/free"
    assert res["intent"] == "CITY_OVERVIEW"
    assert res["tools"][0]["name"] == "get_city_profile"


def test_safety_labels_are_stripped_before_json_parse():
    svc = OpenRouterService()
    svc.model = "openrouter/free"
    mixed = _completion_response(
        'User Safety: safe\nResponse Safety: safe\n{"intent":"COMPARE","agents":["market_agent"],"tools":[{"name":"get_micro_market_profile","arguments":{"market_name":"Kanakapura Road"}}],"clarification_needed":false}',
        "liquid/lfm-2.5-2.6b:free",
    )

    with patch.object(svc, "_refresh_config"), \
         patch.object(svc, "is_configured", return_value=True), \
         patch.object(svc.session, "post", return_value=mixed):
        svc.api_key = "configured-test-key"
        res = svc.structured_completion([{"role": "user", "content": "compare"}], stage="stage1")

    assert res["intent"] == "COMPARE"
    assert res["tools"][0]["arguments"]["market_name"] == "Kanakapura Road"


def test_truncated_comparison_json_is_recovered_and_not_shown_raw():
    svc = OpenRouterService()
    truncated = (
        '{ "intent": "comparative_analysis", "agents": ["market_agent"], "tools": '
        '[ { "name": "get_micro_market_profile", "arguments": {"market_name": "Kanakapura"} }, { "n'
    )
    complete = {
        "content": (
            '{"intent":"comparative_analysis","agents":["market_agent"],"tools":['
            '{"name":"get_micro_market_profile","arguments":{"market_name":"Kanakapura Road"}},'
            '{"name":"get_micro_market_profile","arguments":{"market_name":"Bagalur"}}'
            '],"clarification_needed":false}'
        ),
        "finish_reason": "stop",
    }
    first = {"content": truncated, "finish_reason": "length"}

    with patch.object(svc, "chat_completion", side_effect=[first, complete]) as chat_mock:
        res = svc.structured_completion([{"role": "user", "content": "Compare Kanakapura & Bagalur"}], stage="stage1")

    assert chat_mock.call_count == 2
    assert res["intent"] == "comparative_analysis"
    assert [tool["arguments"]["market_name"] for tool in res["tools"]] == ["Kanakapura Road", "Bagalur"]


def test_truncated_comparison_json_still_runs_when_the_retry_is_cut_off():
    svc = OpenRouterService()
    truncated = (
        '{ "intent": "comparative_analysis", "agents": ["market_agent"], "tools": '
        '[ { "name": "get_micro_market_profile", "arguments": {"market_name": "Kanakapura"} }, { "n'
    )
    with patch.object(svc, "chat_completion", return_value={"content": truncated, "finish_reason": "stop"}):
        res = svc.structured_completion([{"role": "user", "content": "Compare Kanakapura & Bagalur"}], stage="stage1")

    assert res["intent"] == "comparative_analysis"
    assert res["tools"][0]["name"] == "get_micro_market_profile"
    assert res["tools"][0]["arguments"]["market_name"] == "Kanakapura"
    assert "Raw output" not in str(res)


def test_unrecoverable_json_does_not_expose_raw_model_text():
    svc = OpenRouterService()
    with patch.object(svc, "chat_completion", return_value={"content": "not json at all", "finish_reason": "stop"}):
        with pytest.raises(OpenRouterJSONError) as exc_info:
            svc.structured_completion([{"role": "user", "content": "compare"}], stage="stage1")

    message = str(exc_info.value)
    assert "incomplete answer plan" in message
    assert "Raw output" not in message
    assert "not json" not in message


def test_repeated_safety_classifier_is_not_shown_as_the_answer():
    svc = OpenRouterService()
    svc.model = "openrouter/free"
    safety = _completion_response(
        "User Safety: safe Response Safety: safe",
        "nvidia/nemotron-3.5-content-safety:free",
    )

    with patch.object(svc, "_refresh_config"), \
         patch.object(svc, "is_configured", return_value=True), \
         patch.object(svc.session, "post", return_value=safety) as post_mock:
        svc.api_key = "configured-test-key"
        with pytest.raises(OpenRouterError) as exc_info:
            svc.chat_completion([{"role": "user", "content": "compare"}], stage="stage2")

    assert post_mock.call_count == 3
    message = str(exc_info.value)
    assert "content-safety classification" in message
    assert "invalid JSON" not in message
    assert message != "User Safety: safe Response Safety: safe"


def test_unavailable_free_slug_does_not_call_paid_model():
    svc = OpenRouterService()
    svc.model = "qwen/qwen-2.5-7b-instruct:free"
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = (
        '{"error":{"message":"This model is unavailable for free. '
        'The paid version is available now - use this slug instead: qwen/qwen-2.5-7b-instruct","code":404}}'
    )
    mock_resp.headers = {}

    with patch.object(svc, "_refresh_config"), \
         patch.object(svc, "is_configured", return_value=True), \
         patch.object(svc.session, "post", return_value=mock_resp) as post_mock:
        svc.api_key = "configured-test-key"
        with pytest.raises(OpenRouterError) as exc_info:
            svc.chat_completion([{"role": "user", "content": "ping"}], stage="auth_probe")

        assert post_mock.call_count == 1
        assert post_mock.call_args.kwargs["json"]["model"] == "qwen/qwen-2.5-7b-instruct:free"

    assert not isinstance(exc_info.value, OpenRouterAuthError)
    assert not isinstance(exc_info.value, OpenRouterRateLimitError)
    assert "will not switch to the paid model" in str(exc_info.value)


def test_daily_quota_is_not_reported_as_authentication_failure():
    svc = OpenRouterService()
    svc.model = "qwen/qwen-2.5-7b-instruct:free"
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = '{"error":{"message":"free-models-per-day","code":429}}'
    mock_resp.headers = {"X-RateLimit-Remaining": "0"}

    with patch.object(svc, "_refresh_config"), \
         patch.object(svc, "is_configured", return_value=True), \
         patch.object(svc.session, "post", return_value=mock_resp):
        svc.api_key = "configured-test-key"
        with pytest.raises(OpenRouterRateLimitError) as exc_info:
            svc.chat_completion([{"role": "user", "content": "ping"}], stage="auth_probe")

    assert not isinstance(exc_info.value, OpenRouterAuthError)
    assert exc_info.value.category == "daily_quota"
    assert "not an authentication failure" in str(exc_info.value)
    assert mock_resp.text not in str(exc_info.value)


def test_orchestrator_returns_quota_error_without_auth_wording():
    orchestrator = LLMOrchestrator()

    def raise_quota(*args, **kwargs):
        raise OpenRouterRateLimitError(
            "OpenRouter free-model daily quota is exhausted. "
            "The Copilot will not retry this request. "
            "This is a quota limit, not an authentication failure.",
            category="daily_quota",
        )

    with patch.object(orchestrator.openrouter, "is_configured", return_value=True), \
         patch.object(orchestrator.openrouter, "structured_completion", side_effect=raise_quota):
        res = orchestrator.process_query("why not whitefield?")

    assert res["status"] == "error"
    assert res["error_type"] == "llm_quota_exceeded"
    assert "Please check your OpenRouter API key" not in res["answer"]
    assert "not an authentication failure" in res["answer"]


def test_compact_tool_schema_still_executes_allowlisted_tool():
    orchestrator = LLMOrchestrator()
    mock_routing_decision = {
        "intent": "MARKET_ANALYSIS",
        "agents": ["market_agent"],
        "tools": ["get_micro_market_profile"],
        "arguments": {"market_name": "Whitefield"},
        "clarification_needed": False,
    }
    mock_synthesis_response = {
        "content": "Whitefield profile is grounded in the retrieved market evidence.",
        "raw": {},
        "model_used": "qwen/qwen-2.5-7b-instruct:free",
    }

    with patch.object(orchestrator.openrouter, "is_configured", return_value=True), \
         patch.object(orchestrator.openrouter, "structured_completion", return_value=mock_routing_decision), \
         patch.object(orchestrator.openrouter, "chat_completion", return_value=mock_synthesis_response):
        res = orchestrator.process_query("why not whitefield?")

    assert res["status"] == "success"
    assert res["intent"] == "MARKET_ANALYSIS"
    assert "market_agent" in res["agents_used"]
    assert res["tools_used"] == ["get_micro_market_profile"]
    assert res["evidence"][0]["status"] == "success"
    assert res["evidence"][0].get("data")

