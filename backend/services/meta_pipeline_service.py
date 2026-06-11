from __future__ import annotations

import math
import uuid
from typing import Dict, List, Optional, Tuple

from backend.schemas.article import ArticleSections
from backend.schemas.meta import MetaAnalysisResponse, MetaAnalyzeRequest, MetaPipelineStatus
from backend.schemas.statistics import MetaResultMaster, PlotPayload
from backend.schemas.studies import OutcomeExtraction, StudyExtraction
from backend.services.article_generation_service import generate_article_sections
from backend.services.meta_statistics_service import run_meta_statistics
from backend.services.prisma_service import build_prisma_counts
from backend.statistics import StudyEffectInput


def _continuous_inputs(outcome: OutcomeExtraction) -> Tuple[float, float, float, float, int, int]:
    if (
        outcome.intervention_mean is None
        or outcome.comparator_mean is None
        or outcome.intervention_sd is None
        or outcome.comparator_sd is None
        or outcome.intervention_total is None
        or outcome.comparator_total is None
    ):
        raise ValueError("dados contínuos incompletos (mean/SD/N dos dois grupos)")
    n_t = outcome.intervention_total
    n_c = outcome.comparator_total
    if min(n_t, n_c) <= 1:
        raise ValueError("N dos grupos deve ser > 1")
    if outcome.intervention_sd <= 0 or outcome.comparator_sd <= 0:
        raise ValueError("SD deve ser > 0")
    return (
        outcome.intervention_mean,
        outcome.comparator_mean,
        outcome.intervention_sd,
        outcome.comparator_sd,
        n_t,
        n_c,
    )


def _smd_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    """SMD com correção de Hedges (g) para amostras pequenas."""
    mean_t, mean_c, sd_t, sd_c, n_t, n_c = _continuous_inputs(outcome)
    df = n_t + n_c - 2
    sp2 = (((n_t - 1) * (sd_t ** 2)) + ((n_c - 1) * (sd_c ** 2))) / df
    if sp2 <= 0:
        raise ValueError("desvio padrão pooled inválido")
    d = (mean_t - mean_c) / math.sqrt(sp2)
    var_d = (n_t + n_c) / (n_t * n_c) + (d ** 2) / (2 * df)
    j = 1.0 - 3.0 / (4.0 * df - 1.0)
    return j * d, (j ** 2) * var_d


def _md_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    mean_t, mean_c, sd_t, sd_c, n_t, n_c = _continuous_inputs(outcome)
    effect = mean_t - mean_c
    variance = (sd_t ** 2) / n_t + (sd_c ** 2) / n_c
    return effect, variance


def _binary_cells(outcome: OutcomeExtraction) -> Tuple[float, float, float, float]:
    if (
        outcome.intervention_events is None
        or outcome.comparator_events is None
        or outcome.intervention_total is None
        or outcome.comparator_total is None
    ):
        raise ValueError("dados dicotômicos incompletos (eventos/N dos dois grupos)")
    a = float(outcome.intervention_events)
    b = float(outcome.intervention_total - outcome.intervention_events)
    c = float(outcome.comparator_events)
    d = float(outcome.comparator_total - outcome.comparator_events)
    if (a == 0 and c == 0) or (b == 0 and d == 0):
        raise ValueError("estudo sem eventos (ou só eventos) nos dois braços não é informativo para RR/OR")
    # Correção de continuidade apenas quando existe célula zero.
    if min(a, b, c, d) == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    return a, b, c, d


def _log_rr_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    a, b, c, d = _binary_cells(outcome)
    risk_t = a / (a + b)
    risk_c = c / (c + d)
    effect = math.log(risk_t / risk_c)
    variance = (1 / a) - (1 / (a + b)) + (1 / c) - (1 / (c + d))
    return effect, variance


def _log_or_and_variance(outcome: OutcomeExtraction) -> Tuple[float, float]:
    a, b, c, d = _binary_cells(outcome)
    effect = math.log((a * d) / (b * c))
    variance = (1 / a) + (1 / b) + (1 / c) + (1 / d)
    return effect, variance


_EFFECT_BUILDERS = {
    "SMD": _smd_and_variance,
    "MD": _md_and_variance,
    "log_RR": _log_rr_and_variance,
    "log_OR": _log_or_and_variance,
}


def _subgroup_label(study: StudyExtraction, subgroup_variable: Optional[str]) -> Optional[str]:
    field = subgroup_variable or "design"
    value = getattr(study, field, None)
    if value is None:
        return None
    return str(value)


def _build_effect_input(
    studies: List[StudyExtraction],
    effect_measure: str,
    subgroup_variable: Optional[str] = None,
) -> Tuple[List[StudyEffectInput], List[str]]:
    """Um efeito por estudo (primeiro desfecho computável) para evitar dupla contagem."""
    builder = _EFFECT_BUILDERS.get(effect_measure)
    effect_rows: List[StudyEffectInput] = []
    warnings: List[str] = []
    if builder is None:
        warnings.append(f"Medida de efeito não suportada: {effect_measure}.")
        return effect_rows, warnings

    for study in studies:
        chosen: Optional[Tuple[float, float, str]] = None
        last_error = "sem desfechos registrados"
        for outcome in study.outcomes:
            try:
                effect, variance = builder(outcome)
            except Exception as error:
                last_error = str(error)
                continue
            if variance <= 0:
                last_error = "variância calculada não positiva"
                continue
            if chosen is None:
                chosen = (effect, variance, outcome.outcome_name)
            else:
                warnings.append(
                    f"{study.citation}: desfecho adicional '{outcome.outcome_name}' ignorado no pooling "
                    "principal para evitar dupla contagem do mesmo estudo."
                )
        if chosen is None:
            warnings.append(f"{study.citation}: excluído do pooling ({last_error}).")
            continue
        effect, variance, _ = chosen
        effect_rows.append(
            StudyEffectInput(
                study_id=study.study_id,
                citation=study.citation,
                effect=effect,
                variance=variance,
                subgroup=_subgroup_label(study, subgroup_variable),
            )
        )
    return effect_rows, warnings


def analyze_meta(request: MetaAnalyzeRequest) -> MetaAnalysisResponse:
    project_id = request.project_id or f"meta_{uuid.uuid4().hex[:12]}"
    included = [row for row in request.studies if row.included]
    excluded = [row for row in request.studies if not row.included]
    article_sections = ArticleSections()

    effects, warnings = _build_effect_input(
        included,
        effect_measure=request.effect_measure.value,
        subgroup_variable=request.subgroup_variable,
    )
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
            warnings=warnings + ["Pooling quantitativo indisponível por falta de dados completos."],
        )

    stats = run_meta_statistics(
        effects=effects,
        effect_measure=request.effect_measure.value,
        model_used=request.model_used.value,
    )
    prisma = build_prisma_counts(request.studies)
    measure_label = request.effect_measure.value.replace("log_", "")
    narrative = (
        f"Foram incluídos {len(included)} estudos na revisão, dos quais {len(effects)} contribuíram "
        f"para a síntese quantitativa ({measure_label}, modelo {stats['pooled_result'].model}). "
        f"Efeito combinado={stats['pooled_result'].effect:.4f} "
        f"(IC95% {stats['pooled_result'].ci_low:.4f} a {stats['pooled_result'].ci_high:.4f}; "
        f"p={stats['pooled_result'].p_value:.4f}), "
        f"I²={stats['heterogeneity'].I2:.2f}% e p de heterogeneidade={stats['heterogeneity'].p_heterogeneity:.4f}."
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

