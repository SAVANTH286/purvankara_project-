from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.copilot.copilot_service import get_copilot_service
from backend.intelligence.tool_registry import TOOL_CATALOG
from backend.intelligence.agent_registry import list_registered_agents

router = APIRouter(
    prefix="/copilot",
    tags=["AI Copilot"]
)


class ChatMessage(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="What is the absorption situation in Kanakapura Road?")


class ChatRequest(BaseModel):
    message: str = Field(..., example="What is the absorption rate in Kanakapura Road?")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)


@router.post("/chat")
def chat_with_copilot(req: ChatRequest) -> Dict[str, Any]:
    """
    Interacts with the PURAVANKARA AI Copilot via pure LLM-based autonomous orchestration.
    Stage 1 routes to specialized agents and tools.
    Stage 2 synthesizes grounded responses from retrieved evidence.
    """
    try:
        service = get_copilot_service()
        history_dicts = [{"role": m.role, "content": m.content} for m in (req.history or [])]
        result = service.chat(req.message, history_dicts)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot Error: {str(e)}")


@router.get("/tools")
def list_copilot_tools() -> List[Dict[str, Any]]:
    """Returns the list of tools registered with the AI Copilot."""
    return TOOL_CATALOG


@router.get("/agents")
def list_copilot_agents() -> List[Dict[str, Any]]:
    """Returns the list of intelligence agents registered with the AI Copilot."""
    return list_registered_agents()
