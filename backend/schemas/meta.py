from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .article import ArticleSections
from .statistics import (
    EffectSizeRow,
    HeterogeneityResult,
    LeaveOneOutResult,
    MetaResultMaster,
    PlotPayload,
    PooledResult,
    PublicationBiasResult,
    SubgroupResult,
)
from .studies import StudyExtraction


class MetaModel(str, Enum):
    fixed = "fixed"
    random_dl = "random_DL"
    random_reml = "random_REML"
    random_pm = "random_PM"


class EffectMeasure(str, Enum):
    smd = "SMD"
    md = "MD"
    log_rr = "log_RR"
    log_or = "log_OR"


class MetaPipelineStatus(str, Enum):
    success = "success"
    warning = "warning"
    error = "error"


class PrismaCounts(BaseModel):
    identified: int = 0
    screened: int = 0
    eligible: int = 0
    included: int = 0
    excluded_reasons: List[Dict[str, str]] = Field(default_factory=list)


class MetaAnalyzeRequest(BaseModel):
    project_id: Optional[str] = None
    question: str = ""
    effect_measure: EffectMeasure = EffectMeasure.smd
    model_used: MetaModel = MetaModel.random_dl
    studies: List[StudyExtraction] = Field(default_factory=list)
    subgroup_variable: Optional[str] = None
    generate_article: bool = False


class MetaReviewRequest(BaseModel):
    project_id: Optional[str] = None
    studies: List[StudyExtraction] = Field(default_factory=list)


class MetaUploadResponse(BaseModel):
    status: MetaPipelineStatus
    project_id: str
    studies: List[StudyExtraction] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class MetaAnalysisResponse(BaseModel):
    status: MetaPipelineStatus
    project_id: str
    question: str
    effect_measure: str
    model_used: str
    studies_included: List[StudyExtraction] = Field(default_factory=list)
    studies_excluded: List[StudyExtraction] = Field(default_factory=list)
    effects_table: List[EffectSizeRow] = Field(default_factory=list)
    pooled_result: Optional[PooledResult] = None
    heterogeneity: Optional[HeterogeneityResult] = None
    publication_bias: Optional[PublicationBiasResult] = None
    leave_one_out: List[LeaveOneOutResult] = Field(default_factory=list)
    subgroups: List[SubgroupResult] = Field(default_factory=list)
    forest_plot_svg: Optional[str] = None
    funnel_plot_svg: Optional[str] = None
    prisma: PrismaCounts = Field(default_factory=PrismaCounts)
    narrative_results: str = ""
    article_sections: ArticleSections = Field(default_factory=ArticleSections)
    meta_result_master: Optional[MetaResultMaster] = None
    warnings: List[str] = Field(default_factory=list)
    plots: Optional[PlotPayload] = None

