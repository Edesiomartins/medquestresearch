from __future__ import annotations

import math
import uuid
from typing import Dict, List, Tuple

from backend.schemas.article import ArticleSections
from backend.schemas.meta import MetaAnalysisResponse, MetaAnalyzeRequest, MetaPipelineStatus
from backend.schemas.statistics import MetaResultMaster, PlotPayload
from backend.schemas.studies import OutcomeExtraction, StudyExtraction
from backend.services.article_generation_service import generate_article_sections
from backend.services.meta_statistics_service import run_meta_statistics
from backend.services.prisma_service import build_prisma_counts
from backend.statistics import StudyEffectInput


def _smd_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    if (
        outcome.intervention_mean is None
        or outcome.comparator_mean is None
        or outcome.intervention_sd is None
        or outcome.comparator_sd is None
        or outcome.intervention_total is None
        or outcome.comparator_total is None
    ):
        raise ValueError("Dados contínuos incompletos para SMD.")
    n_t = outcome.intervention_total
    n_c = outcome.comparator_total
    if min(n_t, n_c) <= 1:
        raise ValueError("N dos grupos deve ser > 1.")
    sp2 = (((n_t - 1) * (outcome.intervention_sd ** 2)) + ((n_c - 1) * (outcome.comparator_sd ** 2))) / (n_t + n_c - 2)
    if sp2 <= 0:
        raise ValueError("Desvio padrão pooled inválido.")
    effect = (outcome.intervention_mean - outcome.comparator_mean) / math.sqrt(sp2)
    variance = (n_t + n_c) / (n_t * n_c) + (effect ** 2) / (2 * (n_t + n_c - 2))
    return effect, variance


def _log_rr_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    if (
        outcome.intervention_events is None
        or outcome.comparator_events is None
        or outcome.intervention_total is None
        or outcome.comparator_total is None
    ):
        raise ValueError("Dados dicotômicos incompletos para RR.")
    a = outcome.intervention_events + 0.5
    c = outcome.comparator_events + 0.5
    b = (outcome.intervention_total - outcome.intervention_events) + 0.5
    d = (outcome.comparator_total - outcome.comparator_events) + 0.5
    risk_t = a / (a + b)
    risk_c = c / (c + d)
    effect = math.log(risk_t / risk_c)
    variance = (1 / a) - (1 / (a + b)) + (1 / c) - (1 / (c + d))
    return effect, variance


def _log_or_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    if (
        outcome.intervention_events is None
        or outcome.comparator_events is None
        or outcome.intervention_total is None
        or outcome.comparator_total is None
    ):
        raise ValueError("Dados dicotômicos incompletos para OR.")
    a = outcome.intervention_events + 0.5
    c = outcome.comparator_events + 0.5
    b = (outcome.intervention_total - outcome.intervention_events) + 0.5
    d = (outcome.comparator_total - outcome.comparator_events) + 0.5
    effect = math.log((a * d) / (b * c))
    variance = (1 / a) + (1 / b) + (1 / c) + (1 / d)
    return effect, variance


def _build_effect_input(studies: List[StudyExtraction], effect_measure: str) -> List[StudyEffectInput]:
    effect_rows: List[StudyEffectInput] = []
    for study in studies:
        for outcome in study.outcomes:
            try:
                if effect_measure == "SMD":
                    effect, variance = _smd_and_variance(outcome)
                elif effect_measure == "log_RR":
                    effect, variance = _log_rr_and_variance(outcome)
                elif effect_measure == "log_OR":
                    effect, variance = _log_or_and_variance(outcome)
                else:
                    continue
                effect_rows.append(
                    StudyEffectInput(
                        study_id=study.study_id,
                        citation=study.citation,
                        effect=effect,
                        variance=variance,
                        subgroup=study.design,
                    )
                )
            except Exception:
                continue
    return effect_rows


def analyze_meta(request: MetaAnalyzeRequest) -> MetaAnalysisResponse:
    project_id = request.project_id or f"meta_{uuid.uuid4().hex[:12]}"
    included = [row for row in request.studies if row.included]
    excluded = [row for row in request.studies if not row.included]
    warnings: List[str] = []
    article_sections = ArticleSections()

    effects = _build_effect_input(included, effect_measure=request.effect_measure.value)
    if len(effects) < 2:
        prisma = build_prisma_counts(request.studies)
        return MetaAnalysisResponse(
            status=MetaPipelineStatus.warning,
            project_id=project_id,
            question=request.question,
            effect_measure=request.effect_measure.value,
            model_used=request.model_used.value,
            studies_included=included,
            studies_excluded=excluded,
            prisma=prisma,
            narrative_results=(
                "Não há estudos com dados suficientes para pooling quantitativo. "
                "Foi mantida síntese narrativa para preservar validade metodológica."
            ),
            article_sections=article_sections,
            warnings=["Pooling quantitativo indisponível por falta de dados completos."],
        )

    stats = run_meta_statistics(
        effects=effects,
        effect_measure=request.effect_measure.value,
        model_used=request.model_used.value,
    )
    prisma = build_prisma_counts(request.studies)
    narrative = (
        f"Foram incluídos {len(included)} estudos no modelo {stats['pooled_result'].model}. "
        f"Efeito combinado={stats['pooled_result'].effect:.4f} "
        f"(IC95% {stats['pooled_result'].ci_low:.4f} a {stats['pooled_result'].ci_high:.4f}), "
        f"I²={stats['heterogeneity'].I2:.2f}% e p heterogeneidade={stats['heterogeneity'].p_heterogeneity:.4f}."
    )
    response = MetaAnalysisResponse(
        status=MetaPipelineStatus.success,
        project_id=project_id,
        question=request.question,
        effect_measure=request.effect_measure.value,
        model_used=request.model_used.value,
        studies_included=included,
        studies_excluded=excluded,
        effects_table=stats["effects_table"],
        pooled_result=stats["pooled_result"],
        heterogeneity=stats["heterogeneity"],
        publication_bias=stats["publication_bias"],
        leave_one_out=stats["leave_one_out"],
        subgroups=stats["subgroups"],
        forest_plot_svg=stats["forest_plot_svg"],
        funnel_plot_svg=stats["funnel_plot_svg"],
        prisma=prisma,
        narrative_results=narrative,
        warnings=warnings,
        plots=PlotPayload(
            forest_plot_svg=stats["forest_plot_svg"],
            funnel_plot_svg=stats["funnel_plot_svg"],
        ),
    )
    master = MetaResultMaster(
        studies=[row.dict() for row in request.studies],
        included=[row.dict() for row in included],
        excluded=[row.dict() for row in excluded],
        extracted_data=[row.dict() for row in included],
        effects_table=response.effects_table,
        pooled_result=response.pooled_result,
        heterogeneity=response.heterogeneity,
        publication_bias=response.publication_bias,
        leave_one_out=response.leave_one_out,
        subgroup_results=response.subgroups,
        forest_plot_svg=response.forest_plot_svg,
        funnel_plot_svg=response.funnel_plot_svg,
        narrative_summary=response.narrative_results,
        prisma_counts=response.prisma.dict(),
    )
    response.meta_result_master = master

    if request.generate_article:
        response.article_sections = generate_article_sections(response.dict())
    return response

