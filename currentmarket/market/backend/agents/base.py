from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    project_name: str = Field(..., example="Purva Grandeur")
    developer: str = Field("Puravankara", example="Puravankara")
    property_type: str = Field("Residential", example="Residential")
    property_segment: str = Field("Mid", example="Mid")
    location: str = Field(..., example="Kanakapura Road")
    micro_market: str = Field(..., example="Kanakapura Road")
    price_per_sqft: float = Field(..., example=6500.0)
    units: int = Field(..., example=300)
    bhk: Optional[str] = Field("3BHK", example="3BHK")
    launch_date: Optional[str] = Field("2026-10-01", example="2026-10-01")
    include_buyer_intelligence: bool = Field(True, example=True)
    # Optional financial inputs
    land_cost_per_sqft: Optional[float] = None
    construction_cost_per_sqft: Optional[float] = None
    # Optional selected coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AgentEvidence(BaseModel):
    agent_name: str
    status: str = "available"  # "available", "partial", "unavailable"
    decision_bias: str = "neutral"  # "supportive", "neutral", "caution", "adverse"
    score: float = 7.0  # 0.0 to 10.0
    summary: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    tool_used: str = "database_query"
    ml_used: bool = False
    model_used: Optional[str] = None
    confidence: Optional[float] = None  # MUST be null unless validated by ML
    details: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        # Synchronize alias fields
        if not self.key_metrics and self.metrics:
            self.key_metrics = self.metrics
        elif not self.metrics and self.key_metrics:
            self.metrics = self.key_metrics
        if not self.observations and self.evidence:
            self.observations = self.evidence
        elif not self.evidence and self.observations:
            self.evidence = self.observations


class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, project: ProjectInput) -> AgentEvidence:
        raise NotImplementedError
