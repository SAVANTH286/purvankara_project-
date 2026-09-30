import os
import json
import re
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger("PuravankaraOpenRouter")

# Ensure environment variables from .env are reliably found from workspace root
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv(find_dotenv(usecwd=True))


class OpenRouterError(Exception):
    """Base exception for OpenRouter communication errors."""
    pass


class OpenRouterAuthError(OpenRouterError):
    """Raised when API key is missing, invalid, or unauthorized (HTTP 401/403)."""
    pass


class OpenRouterRateLimitError(OpenRouterError):
    """Raised when rate limit or quota is exceeded (HTTP 429). Not an authentication failure."""

    def __init__(self, message: str, category: str = "rate_limit"):
        super().__init__(message)
        self.category = category


class OpenRouterConnectionError(OpenRouterError):
    """Raised when persistent network or SSL connection failure occurs."""
    pass


class OpenRouterJSONError(OpenRouterError):
    """Raised when LLM output cannot be parsed into valid JSON structure."""
    pass


# openrouter/free sometimes routes to a classifier that only emits these labels.
_SAFETY_LABEL_PREFIX = re.compile(
    r"^(?:(?:User|Response)\s+Safety\s*:\s*[A-Za-z_-]+\s*)+",
    re.IGNORECASE,
)


def _strip_safety_labels(text: str) -> str:
    """Remove a leading content-safety classification. Leave any real answer."""
    return _SAFETY_LABEL_PREFIX.sub("", (text or "").strip()).strip()


def _is_safety_classifier_model(model_name: str) -> bool:
    lowered = (model_name or "").lower()
    return "content-safety" in lowered or "safety-guard" in lowered


def _odd_unescaped_quotes(text: str) -> bool:
    count = 0
    escaped = False
    for ch in text:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            count += 1
    return count % 2 == 1


def _close_json_fragment(fragment: str) -> str:
    """Close a truncated JSON object without inventing keys."""
    snippet = fragment.rstrip()
    if snippet.endswith("```"):
        snippet = snippet[:-3].rstrip()
    snippet = re.sub(r",\s*$", "", snippet)
    if _odd_unescaped_quotes(snippet):
        snippet += '"'
        snippet = re.sub(r",\s*$", "", snippet)
    if re.search(r":\s*$", snippet):
        snippet += "null"
    open_curly = snippet.count("{") - snippet.count("}")
    open_square = snippet.count("[") - snippet.count("]")
    if open_curly < 0 or open_square < 0:
        return snippet
    return snippet + ("]" * open_square) + ("}" * open_curly)


def _salvage_structured_json(content: str) -> Optional[Dict[str, Any]]:
    """
    Recover a routing plan when the model stops mid-object.
    Keeps the longest prefix that still contains intent, agents, or tools.
    """
    start = content.find("{")
    if start < 0:
        return None
    blob = content[start:].strip()
    if blob.endswith("```"):
        blob = blob[:-3].strip()

    cut_points = [index for index, ch in enumerate(blob) if ch in "{}[]"]
    if not cut_points:
        return None

    for index in reversed(cut_points):
        closed = _close_json_fragment(blob[:index + 1])
        try:
            parsed = json.loads(closed)
        except Exception:
            continue
        if isinstance(parsed, dict) and ("intent" in parsed or "tools" in parsed or "agents" in parsed):
            return parsed
    return None


class OpenRouterService:
    def __init__(self):
        self.session: Optional[requests.Session] = None
        self._refresh_config()

    def _refresh_config(self):
        if ENV_PATH.exists():
            load_dotenv(dotenv_path=ENV_PATH, override=True)
        else:
            load_dotenv(find_dotenv(usecwd=True), override=True)

        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().rstrip("/")

        if self.session is None:
            self.session = requests.Session()

    def _reset_session(self):
        """Recreates the connection pool if a connection reset or SSLEOFError occurs."""
        try:
            if self.session:
                self.session.close()
        except Exception:
            pass
        self.session = requests.Session()

    def is_configured(self) -> bool:
        self._refresh_config()
        return bool(self.api_key and len(self.api_key) > 8)

    def _rate_limit_details(self, resp: requests.Response) -> tuple:
        """Classify HTTP 429 without logging response bodies or credentials."""
        body = ""
        try:
            body = resp.text or ""
        except Exception:
            body = ""
        lowered = body.lower()
        remaining = (resp.headers.get("X-RateLimit-Remaining") or "").strip()
        daily = (
            "free-models-per-day" in lowered
            or "per-day" in lowered
            or "daily" in lowered and "quota" in lowered
            or (remaining == "0" and "free" in lowered)
        )
        if daily:
            return (
                "daily_quota",
                "OpenRouter free-model daily quota is exhausted. "
                "The Copilot will not retry this request. "
                "This is a quota limit, not an authentication failure.",
            )
        return (
            "rate_limit",
            "OpenRouter rate limit exceeded. "
            "The Copilot will not retry this request. "
            "This is a rate limit, not an authentication failure.",
        )

    def _log_call(self, stage: str, http_status: Any, latency_ms: int, error_category: str = "ok") -> None:
        logger.info(
            "OpenRouter call model=%s http_status=%s stage=%s latency_ms=%s error_category=%s",
            self.model,
            http_status,
            stage,
            latency_ms,
            error_category,
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 35,
        stage: str = "completion",
    ) -> Dict[str, Any]:
        """
        Executes a standard or structured chat completion via OpenRouter API with
        custom browser-grade User-Agent and bounded transient network/SSL retries.
        """
        self._refresh_config()
        if not self.is_configured():
            raise OpenRouterAuthError("OpenRouter API key is missing or not configured in environment.")

        token_limit = max_tokens or int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://puravankara.com",
            "X-Title": "Puravankara AI Decision Intelligence",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 PuravankaraAI/2.5"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": token_limit
        }

        if response_format:
            payload["response_format"] = response_format

        max_retries = 2
        max_safety_retries = 2
        started = time.perf_counter()
        resp = None

        for safety_attempt in range(max_safety_retries + 1):
            for attempt in range(max_retries + 1):
                try:
                    resp = self.session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=timeout
                    )
                    break
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    logger.warning(
                        "Transient connection error to OpenRouter on attempt %s/%s model=%s stage=%s latency_ms=%s error_category=connection exception_type=%s",
                        attempt + 1,
                        max_retries + 1,
                        self.model,
                        stage,
                        latency_ms,
                        type(e).__name__,
                    )
                    self._reset_session()
                    if attempt < max_retries:
                        time.sleep(0.5 * (attempt + 1))
                    else:
                        self._log_call(stage, "connection", latency_ms, "connection")
                        raise OpenRouterConnectionError(f"Network/SSL connection failure connecting to OpenRouter: {type(e).__name__}")
                except Exception as e:
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    self._log_call(stage, "connection", latency_ms, "connection")
                    raise OpenRouterError(f"Unexpected connection failure to OpenRouter: {type(e).__name__}")

            # A missing free slug must stop here. Never retry a paid or alternate model.
            if resp.status_code == 404:
                latency_ms = int((time.perf_counter() - started) * 1000)
                self._log_call(stage, resp.status_code, latency_ms, "model_unavailable")
                raise OpenRouterError(
                    "The configured free OpenRouter model is unavailable. "
                    "The Copilot will not switch to the paid model automatically."
                )

            latency_ms = int((time.perf_counter() - started) * 1000)

            if resp.status_code in [401, 403]:
                self._log_call(stage, resp.status_code, latency_ms, "authentication")
                raise OpenRouterAuthError("Invalid or expired OpenRouter API key.")
            elif resp.status_code == 429:
                category, message = self._rate_limit_details(resp)
                self._log_call(stage, resp.status_code, latency_ms, category)
                raise OpenRouterRateLimitError(message, category=category)
            elif resp.status_code != 200:
                self._log_call(stage, resp.status_code, latency_ms, "api_error")
                raise OpenRouterError(f"OpenRouter API error ({resp.status_code}).")

            try:
                data = resp.json()
                if "error" in data:
                    err_obj = data["error"]
                    err_msg = err_obj.get("message") if isinstance(err_obj, dict) else str(err_obj)
                    err_code = err_obj.get("code") if isinstance(err_obj, dict) else None
                    err_lower = err_msg.lower()
                    if err_code == 429 or "rate limit" in err_lower or "quota" in err_lower or "free-models-per-day" in err_lower:
                        category = "daily_quota" if ("free-models-per-day" in err_lower or "per-day" in err_lower) else "rate_limit"
                        self._log_call(stage, resp.status_code, latency_ms, category)
                        if category == "daily_quota":
                            message = (
                                "OpenRouter free-model daily quota is exhausted. "
                                "The Copilot will not retry this request. "
                                "This is a quota limit, not an authentication failure."
                            )
                        else:
                            message = (
                                "OpenRouter rate limit exceeded. "
                                "The Copilot will not retry this request. "
                                "This is a rate limit, not an authentication failure."
                            )
                        raise OpenRouterRateLimitError(message, category=category)
                    elif err_code in [401, 403] or "auth" in err_lower or "api key" in err_lower:
                        self._log_call(stage, resp.status_code, latency_ms, "authentication")
                        raise OpenRouterAuthError("OpenRouter authentication failure.")
                    else:
                        self._log_call(stage, resp.status_code, latency_ms, "api_error")
                        raise OpenRouterError("OpenRouter API error.")

                choice = data["choices"][0]["message"]
                content = choice.get("content")
                reasoning = choice.get("reasoning") or choice.get("reasoning_content") or ""
                if content is None:
                    content = reasoning or ""

                cleaned = str(content)
                # 1. Strip explicit <think>...</think> tags
                cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
                # 2. Strip planning monologue if reasoning was emitted before markdown content
                if re.search(r'\n#+\s+', cleaned) and re.match(r'^(We need|Need |Let\'s formulate|Drafting)', cleaned.strip(), re.IGNORECASE):
                    match = re.search(r'\n(#+\s+.*)', cleaned, flags=re.DOTALL)
                    if match:
                        cleaned = match.group(1).strip()

                usable = _strip_safety_labels(cleaned)
                safety_only = bool(cleaned.strip()) and not usable
                if safety_only and reasoning and str(reasoning).strip() != cleaned.strip():
                    usable = _strip_safety_labels(str(reasoning))
                    safety_only = not usable

                routed_model = data.get("model") or self.model
                if safety_only or _is_safety_classifier_model(routed_model):
                    if safety_attempt < max_safety_retries:
                        logger.warning(
                            "OpenRouter returned a content-safety classification model=%s routed_model=%s stage=%s attempt=%s/%s",
                            self.model,
                            routed_model,
                            stage,
                            safety_attempt + 1,
                            max_safety_retries + 1,
                        )
                        continue
                    self._log_call(stage, resp.status_code, latency_ms, "safety_classifier")
                    raise OpenRouterError(
                        "The free model router returned a content-safety classification instead of an answer. Please try again."
                    )

                self._log_call(stage, resp.status_code, latency_ms, "ok")
                return {
                    "content": usable or cleaned or str(content),
                    "raw": data,
                    "model_used": routed_model,
                    "finish_reason": (data.get("choices") or [{}])[0].get("finish_reason"),
                }
            except (OpenRouterError, OpenRouterAuthError, OpenRouterRateLimitError):
                raise
            except Exception:
                self._log_call(stage, getattr(resp, "status_code", "parse"), latency_ms, "parse_error")
                raise OpenRouterError("Failed to parse OpenRouter response JSON.")

    def structured_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        timeout: int = 35,
        stage: str = "stage1",
    ) -> Dict[str, Any]:
        """
        Executes completion requesting JSON format and robustly parses the response.
        Handles thinking tokens, markdown code blocks, and minor syntax anomalies.
        """
        res = self.chat_completion(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            timeout=timeout,
            stage=stage,
        )
        parsed, truncated = self._interpret_structured_content(res.get("content") or "", stage=stage)
        if not isinstance(parsed, dict):
            parsed, truncated = None, True
        # A cutoff plan can drop the second market in a comparison. Ask once more,
        # then keep whichever plan has the completed tools.
        if parsed is None or truncated or res.get("finish_reason") == "length":
            logger.warning(
                "OpenRouter JSON plan was incomplete stage=%s finish_reason=%s; requesting one replacement",
                stage,
                res.get("finish_reason"),
            )
            try:
                retry = self.chat_completion(
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    max_tokens=max_tokens,
                    timeout=timeout,
                    stage=stage,
                )
            except OpenRouterRateLimitError:
                raise
            except OpenRouterError:
                retry = None
            if retry is not None:
                retried, _retried_truncated = self._interpret_structured_content(retry.get("content") or "", stage=stage)
                if self._prefer_plan(retried, parsed):
                    parsed = retried
        if isinstance(parsed, dict):
            return parsed
        raise OpenRouterJSONError(
            "The model returned an incomplete answer plan. Please try again."
        )

    @staticmethod
    def _plan_score(plan: Optional[Dict[str, Any]]) -> int:
        if not isinstance(plan, dict):
            return -1
        tools = plan.get("tools")
        if isinstance(tools, list):
            return len(tools)
        return 1 if plan.get("intent") or plan.get("agents") else 0

    def _prefer_plan(self, candidate: Optional[Dict[str, Any]], current: Optional[Dict[str, Any]]) -> bool:
        return self._plan_score(candidate) > self._plan_score(current)

    def _interpret_structured_content(self, raw_content: str, stage: str = "stage1"):
        content = (raw_content or "").strip()

        # 1. Strip reasoning blocks if present (<think>...</think>)
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

        # 2. Clean markdown code wrapping if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        if not content:
            return None, True

        def _unwrap(parsed):
            if isinstance(parsed, dict) and "tools" not in parsed and "intent" not in parsed:
                for k, v in parsed.items():
                    if isinstance(v, dict) and ("tools" in v or "intent" in v or "agents" in v):
                        return v
            return parsed

        # 3. Direct JSON parse attempt
        try:
            return _unwrap(json.loads(content)), False
        except Exception:
            pass

        # 4. Search for markdown code block embedded anywhere
        markdown_matches = re.findall(r'```(?:json)?\s*([\{\[].*?[\}\]])\s*```', content, re.DOTALL)
        for block in markdown_matches:
            try:
                return _unwrap(json.loads(block.strip())), False
            except Exception:
                pass

        # 5. Extract outermost JSON object between first '{' and last '}'
        start_brace = content.find('{')
        end_brace = content.rfind('}')
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            candidate = content[start_brace:end_brace + 1].strip()
            try:
                return _unwrap(json.loads(candidate)), False
            except Exception:
                # Remove trailing commas before closing braces/brackets
                fixed = re.sub(r',\s*([\}\]])', r'\1', candidate)
                try:
                    return _unwrap(json.loads(fixed)), False
                except Exception:
                    pass

        # 6. Extract outermost JSON array between first '[' and last ']'
        start_bracket = content.find('[')
        end_bracket = content.rfind(']')
        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            candidate = content[start_bracket:end_bracket + 1].strip()
            try:
                parsed_array = json.loads(candidate)
            except Exception:
                fixed = re.sub(r',\s*([\}\]])', r'\1', candidate)
                try:
                    parsed_array = json.loads(fixed)
                except Exception:
                    parsed_array = None
            # Ignore slices such as ["market_agent"] taken from inside a truncated object.
            if isinstance(parsed_array, list) and parsed_array and all(isinstance(item, dict) for item in parsed_array):
                return parsed_array, False

        # 7. Auto-repair unbalanced quotes or brackets on candidate starting from first '{' or '['
        start_idx = -1
        if start_brace != -1 and start_bracket != -1:
            start_idx = min(start_brace, start_bracket)
        elif start_brace != -1:
            start_idx = start_brace
        elif start_bracket != -1:
            start_idx = start_bracket

        if start_idx != -1:
            repaired = content[start_idx:].strip()
            if repaired.endswith("```"):
                repaired = repaired[:-3].strip()

            # Balance quotes
            quotes = [i for i, c in enumerate(repaired) if c == '"' and (i == 0 or repaired[i-1] != '\\')]
            if len(quotes) % 2 != 0:
                repaired += '"'

            open_curly = repaired.count('{') - repaired.count('}')
            open_square = repaired.count('[') - repaired.count(']')
            cand_repaired = re.sub(r',\s*([\}\]])', r'\1', repaired)
            cand_repaired = re.sub(r',\s*$', '', cand_repaired) + (']' * max(0, open_square)) + ('}' * max(0, open_curly))
            try:
                return _unwrap(json.loads(cand_repaired)), False
            except Exception:
                pass

        salvaged = _salvage_structured_json(content)
        if isinstance(salvaged, dict):
            logger.warning(
                "Salvaged truncated orchestration JSON stage=%s chars=%s",
                stage,
                len(content),
            )
            return _unwrap(salvaged), True
        return None, True


_openrouter_service: Optional[OpenRouterService] = None


def get_openrouter_service() -> OpenRouterService:
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService()
    return _openrouter_service
