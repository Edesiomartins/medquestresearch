from __future__ import annotations

import math
from typing import List, Optional

from backend.schemas.statistics import (
    EffectSizeRow,
    HeterogeneityResult,
    LeaveOneOutResult,
    PooledResult,
    PublicationBiasResult,
    SubgroupResult,
)
from backend.statistics import (
    StudyEffectInput,
    compute_effect_table,
    compute_meta_analysis,
    compute_publication_bias,
    compute_subgroups,
    funnel_plot_svg,
    forest_plot_svg,
    leave_one_out_analysis,
)


def _scale_effect(value: float, effect_measure: str) -> float:
    if effect_measure in {"log_RR", "log_OR"}:
        return math.exp(value)
    return value


def run_meta_statistics(
    effects: List[StudyEffectInput],
    effect_measure: str,
    model_used: str,
) -> dict:
    result = compute_meta_analysis(effects, model=model_used)
    table_raw = compute_effect_table(effects, result, effect_measure=effect_measure)

    effects_table = [EffectSizeRow(**row) for row in table_raw]
    pooled = PooledResult(
        effect=_scale_effect(result.pooled_effect, effect_measure),
        ci_low=_scale_effect(result.ci_low, effect_measure),
        ci_high=_scale_effect(result.ci_high, effect_measure),
        se=result.se,
        z_value=result.z_value,
        p_value=result.p_value,
        model=result.model,
        effect_measure=effect_measure,
        k=len(effects),
    )
    heterogeneity = HeterogeneityResult(
        Q=result.Q,
        df=result.df,
        I2=result.I2,
        tau2=result.tau2,
        p_heterogeneity=result.p_heterogeneity,
    )
    bias_raw = compute_publication_bias(effects)
    publication_bias = PublicationBiasResult(**bias_raw)
    loo_raw = leave_one_out_analysis(effects, model=result.model, base_effect=result.pooled_effect)
    leave_one_out = [LeaveOneOutResult(**row) for row in loo_raw]
    subgroup_raw = compute_subgroups(effects, model=result.model, effect_measure=effect_measure)
    subgroups = [SubgroupResult(**row) for row in subgroup_raw]
    forest_svg = forest_plot_svg(table_raw, pooled.dict(), effect_measure=effect_measure)
    funnel_svg = funnel_plot_svg(table_raw, pooled_effect=pooled.effect)

    return {
        "effects_table": effects_table,
        "pooled_result": pooled,
        "heterogeneity": heterogeneity,
        "publication_bias": publication_bias,
        "leave_one_out": leave_one_out,
        "subgroups": subgroups,
        "forest_plot_svg": forest_svg,
        "funnel_plot_svg": funnel_svg,
    }

