from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EffectSizeRow(BaseModel):
    study_id: str
    citation: str
    effect_measure: str
    effect: float
    variance: float
    standard_error: float
    ci_low: float
    ci_high: float
    weight_fixed: Optional[float] = None
    weight_random: Optional[float] = None
    subgroup: Optional[str] = None


class PooledResult(BaseModel):
    effect: float
    ci_low: float
    ci_high: float
    se: float
    z_value: float
    p_value: float
    model: str
    effect_measure: str
    k: int


class HeterogeneityResult(BaseModel):
    Q: float
    df: int
    I2: float
    tau2: float
    p_heterogeneity: float


class PublicationBiasResult(BaseModel):
    egger_p: Optional[float] = None
    begg_p: Optional[float] = None
    interpretation: str = ""


class LeaveOneOutResult(BaseModel):
    removed_study_id: str
    pooled_effect: float
    pooled_ci_low: float
    pooled_ci_high: float
    I2: float
    delta_effect: float


class SubgroupResult(BaseModel):
    subgroup: str
    pooled_result: PooledResult
    heterogeneity: HeterogeneityResult
    studies: List[str]


class PlotPayload(BaseModel):
    forest_plot_svg: Optional[str] = None
    funnel_plot_svg: Optional[str] = None


class MetaResultMaster(BaseModel):
    studies: List[Dict] = Field(default_factory=list)
    included: List[Dict] = Field(default_factory=list)
    excluded: List[Dict] = Field(default_factory=list)
    extracted_data: List[Dict] = Field(default_factory=list)
    effects_table: List[EffectSizeRow] = Field(default_factory=list)
    pooled_result: Optional[PooledResult] = None
    heterogeneity: Optional[HeterogeneityResult] = None
    publication_bias: Optional[PublicationBiasResult] = None
    leave_one_out: List[LeaveOneOutResult] = Field(default_factory=list)
    subgroup_results: List[SubgroupResult] = Field(default_factory=list)
    forest_plot_svg: Optional[str] = None
    funnel_plot_svg: Optional[str] = None
    narrative_summary: Optional[str] = None
    prisma_counts: Dict = Field(default_factory=dict)

