from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class OutcomeExtraction(BaseModel):
    outcome_id: str = Field(..., description="Identificador canônico do desfecho.")
    outcome_name: str
    outcome_type: str = Field(
        default="continuous",
        description="continuous|binary|generic",
    )
    measure_type: Optional[str] = None
    timepoint: Optional[str] = None
    adjusted: bool = False
    intervention_mean: Optional[float] = None
    intervention_sd: Optional[float] = None
    intervention_events: Optional[int] = None
    intervention_total: Optional[int] = None
    comparator_mean: Optional[float] = None
    comparator_sd: Optional[float] = None
    comparator_events: Optional[int] = None
    comparator_total: Optional[int] = None
    effect_candidate: Optional[str] = None
    evidence_snippets: List[str] = Field(default_factory=list)
    page_hints: List[str] = Field(default_factory=list)
    confidence_flags: Dict[str, Any] = Field(default_factory=dict)
    needs_user_confirmation: bool = True

    @validator("outcome_type")
    def validate_outcome_type(cls, value: str) -> str:
        allowed = {"continuous", "binary", "generic"}
        if value not in allowed:
            raise ValueError(f"outcome_type inválido: {value}")
        return value


class StudyExtraction(BaseModel):
    study_id: str
    citation: str
    year: Optional[int] = None
    country: Optional[str] = None
    design: Optional[str] = None
    sample_size: Optional[int] = None
    arms: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)
    comparators: List[str] = Field(default_factory=list)
    follow_up: Optional[str] = None
    risk_of_bias: Optional[str] = None
    outcomes: List[OutcomeExtraction] = Field(default_factory=list)
    evidence_snippets: List[str] = Field(default_factory=list)
    page_hints: List[str] = Field(default_factory=list)
    confidence_flags: Dict[str, Any] = Field(default_factory=dict)
    needs_user_confirmation: bool = True
    included: bool = True
    exclusion_reason: Optional[str] = None

