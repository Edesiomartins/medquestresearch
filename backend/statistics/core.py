from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    from scipy import stats as scipy_stats  # type: ignore
except Exception:
    scipy_stats = None


def _norm_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _norm_sf(value: float) -> float:
    return 1.0 - _norm_cdf(value)


def _chi2_sf(value: float, dof: int) -> float:
    if dof <= 0:
        return 1.0
    if scipy_stats is not None:
        return float(scipy_stats.chi2.sf(value, dof))
    # Aproximação Wilson-Hilferty quando scipy não estiver disponível.
    z = ((value / dof) ** (1 / 3) - (1 - 2 / (9 * dof))) / math.sqrt(2 / (9 * dof))
    return _norm_sf(z)


def _t_sf(value: float, dof: int) -> float:
    if dof <= 0:
        return _norm_sf(value)
    if scipy_stats is not None:
        return float(scipy_stats.t.sf(value, dof))
    return _norm_sf(value)


@dataclass
class StudyEffectInput:
    study_id: str
    citation: str
    effect: float
    variance: float
    subgroup: Optional[str] = None


@dataclass
class MetaComputationResult:
    model: str
    pooled_effect: float
    pooled_variance: float
    se: float
    ci_low: float
    ci_high: float
    z_value: float
    p_value: float
    Q: float
    df: int
    I2: float
    tau2: float
    p_heterogeneity: float
    weights_fixed: List[float]
    weights_random: List[float]


def _validate_effects(effects: List[StudyEffectInput]) -> None:
    if len(effects) < 2:
        raise ValueError("Meta-análise requer pelo menos 2 estudos.")
    for item in effects:
        if item.variance <= 0:
            raise ValueError(f"Variância inválida para estudo {item.study_id}.")


def _fixed_components(effects: List[StudyEffectInput]) -> Tuple[float, float, float, int, List[float]]:
    weights = [1.0 / row.variance for row in effects]
    sum_w = sum(weights)
    mu = sum(w * row.effect for w, row in zip(weights, effects)) / sum_w
    Q = sum(w * ((row.effect - mu) ** 2) for w, row in zip(weights, effects))
    df = len(effects) - 1
    return mu, Q, sum_w, df, weights


def _tau2_dl(effects: List[StudyEffectInput], q_value: float, df: int) -> float:
    weights = [1.0 / row.variance for row in effects]
    sum_w = sum(weights)
    sum_w2 = sum(w * w for w in weights)
    c_value = sum_w - (sum_w2 / sum_w)
    if c_value <= 0:
        return 0.0
    return max(0.0, (q_value - df) / c_value)


def _q_with_tau2(effects: List[StudyEffectInput], tau2: float) -> float:
    weights = [1.0 / (row.variance + tau2) for row in effects]
    sum_w = sum(weights)
    mu = sum(w * row.effect for w, row in zip(weights, effects)) / sum_w
    return sum(w * ((row.effect - mu) ** 2) for w, row in zip(weights, effects))


def _tau2_pm(effects: List[StudyEffectInput], df: int) -> float:
    low, high = 0.0, 10.0
    while _q_with_tau2(effects, high) > df and high < 1e6:
        high *= 2.0
    for _ in range(80):
        mid = (low + high) / 2.0
        q_mid = _q_with_tau2(effects, mid)
        if q_mid > df:
            low = mid
        else:
            high = mid
    return max(0.0, high)


def _tau2_reml(effects: List[StudyEffectInput], initial: float = 0.0) -> float:
    tau2 = max(0.0, initial)
    for _ in range(100):
        weights = [1.0 / (row.variance + tau2) for row in effects]
        sum_w = sum(weights)
        mu = sum(w * row.effect for w, row in zip(weights, effects)) / sum_w
        score = sum(((row.effect - mu) ** 2 - (row.variance + tau2)) / ((row.variance + tau2) ** 2) for row in effects)
        info = sum(1.0 / ((row.variance + tau2) ** 2) for row in effects)
        if info <= 0:
            break
        step = score / info
        new_tau2 = max(0.0, tau2 + step)
        if abs(new_tau2 - tau2) < 1e-10:
            tau2 = new_tau2
            break
        tau2 = new_tau2
    return max(0.0, tau2)


def compute_meta_analysis(effects: List[StudyEffectInput], model: str = "random_DL") -> MetaComputationResult:
    _validate_effects(effects)
    mu_fixed, q_value, _, df, weights_fixed = _fixed_components(effects)

    tau2 = 0.0
    normalized = model.lower()
    if normalized in {"random_dl", "random"}:
        tau2 = _tau2_dl(effects, q_value, df)
        model_name = "random_DL"
    elif normalized in {"random_reml", "reml"}:
        tau2 = _tau2_reml(effects, initial=_tau2_dl(effects, q_value, df))
        model_name = "random_REML"
    elif normalized in {"random_pm", "paule_mandel", "pm"}:
        tau2 = _tau2_pm(effects, df)
        model_name = "random_PM"
    else:
        model_name = "fixed"
        tau2 = 0.0

    weights_random = [1.0 / (row.variance + tau2) for row in effects]
    sum_wr = sum(weights_random)
    mu = sum(w * row.effect for w, row in zip(weights_random, effects)) / sum_wr
    pooled_variance = 1.0 / sum_wr
    se = math.sqrt(pooled_variance)
    z_value = mu / se if se > 0 else 0.0
    p_value = max(0.0, min(1.0, 2.0 * _norm_sf(abs(z_value))))
    ci_low = mu - 1.96 * se
    ci_high = mu + 1.96 * se
    i2 = max(0.0, ((q_value - df) / q_value) * 100.0) if q_value > 0 and df > 0 else 0.0
    p_heterogeneity = _chi2_sf(q_value, df)

    return MetaComputationResult(
        model=model_name,
        pooled_effect=mu,
        pooled_variance=pooled_variance,
        se=se,
        ci_low=ci_low,
        ci_high=ci_high,
        z_value=z_value,
        p_value=p_value,
        Q=q_value,
        df=df,
        I2=i2,
        tau2=tau2,
        p_heterogeneity=p_heterogeneity,
        weights_fixed=weights_fixed,
        weights_random=weights_random,
    )


def compute_effect_table(
    effects: List[StudyEffectInput],
    model_result: MetaComputationResult,
    effect_measure: str,
) -> List[Dict]:
    rows: List[Dict] = []
    for index, item in enumerate(effects):
        se = math.sqrt(item.variance)
        rows.append(
            {
                "study_id": item.study_id,
                "citation": item.citation,
                "effect_measure": effect_measure,
                "effect": item.effect,
                "variance": item.variance,
                "standard_error": se,
                "ci_low": item.effect - 1.96 * se,
                "ci_high": item.effect + 1.96 * se,
                "weight_fixed": model_result.weights_fixed[index],
                "weight_random": model_result.weights_random[index],
                "subgroup": item.subgroup,
            }
        )
    return rows


def leave_one_out_analysis(
    effects: List[StudyEffectInput],
    model: str,
    base_effect: float,
) -> List[Dict]:
    rows: List[Dict] = []
    for item in effects:
        subset = [row for row in effects if row.study_id != item.study_id]
        if len(subset) < 2:
            continue
        pooled = compute_meta_analysis(subset, model=model)
        rows.append(
            {
                "removed_study_id": item.study_id,
                "pooled_effect": pooled.pooled_effect,
                "pooled_ci_low": pooled.ci_low,
                "pooled_ci_high": pooled.ci_high,
                "I2": pooled.I2,
                "delta_effect": pooled.pooled_effect - base_effect,
            }
        )
    rows.sort(key=lambda x: abs(x["delta_effect"]), reverse=True)
    return rows


def compute_publication_bias(effects: List[StudyEffectInput]) -> Dict:
    if len(effects) < 3:
        return {
            "egger_p": None,
            "begg_p": None,
            "interpretation": "Poucos estudos para testar viés de publicação com segurança.",
        }

    se = [math.sqrt(row.variance) for row in effects]
    precision = [1.0 / value for value in se]
    std_effect = [row.effect / value for row, value in zip(effects, se)]
    n = len(effects)

    sum_x = sum(precision)
    sum_y = sum(std_effect)
    sum_xx = sum(x * x for x in precision)
    sum_xy = sum(x * y for x, y in zip(precision, std_effect))
    denom = n * sum_xx - (sum_x * sum_x)
    if denom == 0:
        return {"egger_p": None, "begg_p": None, "interpretation": "Não foi possível calcular Egger/Begg."}

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    residuals = [y - (intercept + slope * x) for x, y in zip(precision, std_effect)]
    rss = sum(r * r for r in residuals)
    variance = rss / max(1, n - 2)
    intercept_se = math.sqrt(variance * (sum_xx / denom))
    t_value = intercept / intercept_se if intercept_se > 0 else 0.0
    egger_p = max(0.0, min(1.0, 2.0 * _t_sf(abs(t_value), max(1, n - 2))))

    begg_p = None
    if scipy_stats is not None:
        tau, begg_p = scipy_stats.kendalltau([row.effect for row in effects], se)  # type: ignore
        _ = tau

    interpretation = "Sem evidência forte de viés de publicação."
    if egger_p is not None and egger_p < 0.1:
        interpretation = "Assimetria potencial de funnel plot; interpretar resultados com cautela."

    return {
        "egger_p": egger_p,
        "begg_p": float(begg_p) if begg_p is not None else None,
        "interpretation": interpretation,
    }


def compute_subgroups(
    effects: List[StudyEffectInput],
    model: str,
    effect_measure: str,
) -> List[Dict]:
    groups: Dict[str, List[StudyEffectInput]] = {}
    for item in effects:
        if not item.subgroup:
            continue
        groups.setdefault(item.subgroup, []).append(item)

    results: List[Dict] = []
    for subgroup, rows in groups.items():
        if len(rows) < 2:
            continue
        pooled = compute_meta_analysis(rows, model=model)
        results.append(
            {
                "subgroup": subgroup,
                "pooled_result": {
                    "effect": pooled.pooled_effect,
                    "ci_low": pooled.ci_low,
                    "ci_high": pooled.ci_high,
                    "se": pooled.se,
                    "z_value": pooled.z_value,
                    "p_value": pooled.p_value,
                    "model": pooled.model,
                    "effect_measure": effect_measure,
                    "k": len(rows),
                },
                "heterogeneity": {
                    "Q": pooled.Q,
                    "df": pooled.df,
                    "I2": pooled.I2,
                    "tau2": pooled.tau2,
                    "p_heterogeneity": pooled.p_heterogeneity,
                },
                "studies": [row.study_id for row in rows],
            }
        )
    return results


def forest_plot_svg(effects_rows: List[Dict], pooled: Dict, effect_measure: str) -> str:
    width, height = 940, max(280, 130 + len(effects_rows) * 26)
    plot_left, plot_right = 300, 860
    baseline = 1.0 if "RR" in effect_measure or "OR" in effect_measure else 0.0

    min_x = min([row["ci_low"] for row in effects_rows] + [pooled["ci_low"], baseline])
    max_x = max([row["ci_high"] for row in effects_rows] + [pooled["ci_high"], baseline])
    pad = (max_x - min_x) * 0.1 if max_x > min_x else 1.0
    min_x -= pad
    max_x += pad

    def x_map(value: float) -> float:
        if max_x == min_x:
            return (plot_left + plot_right) / 2
        return plot_left + ((value - min_x) / (max_x - min_x)) * (plot_right - plot_left)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<text x="24" y="30" font-size="16" font-family="Arial" fill="#0f172a">Forest Plot</text>',
        f'<line x1="{plot_left}" y1="48" x2="{plot_right}" y2="48" stroke="#334155" />',
        f'<line x1="{x_map(baseline)}" y1="48" x2="{x_map(baseline)}" y2="{height - 40}" stroke="#94a3b8" stroke-dasharray="4 4" />',
    ]

    for index, row in enumerate(effects_rows):
        y = 80 + index * 26
        lines.extend(
            [
                f'<text x="24" y="{y + 4}" font-size="12" font-family="Arial" fill="#334155">{row["citation"]}</text>',
                f'<line x1="{x_map(row["ci_low"])}" y1="{y}" x2="{x_map(row["ci_high"])}" y2="{y}" stroke="#2563eb" stroke-width="1.4" />',
                f'<circle cx="{x_map(row["effect"])}" cy="{y}" r="3" fill="#1d4ed8" />',
            ]
        )

    pooled_y = 92 + len(effects_rows) * 26
    lines.extend(
        [
            f'<text x="24" y="{pooled_y + 4}" font-size="12" font-family="Arial" fill="#111827">Pooled</text>',
            f'<line x1="{x_map(pooled["ci_low"])}" y1="{pooled_y}" x2="{x_map(pooled["ci_high"])}" y2="{pooled_y}" stroke="#dc2626" stroke-width="2" />',
            f'<polygon points="{x_map(pooled["effect"])-6},{pooled_y} {x_map(pooled["effect"])},{pooled_y-6} {x_map(pooled["effect"])+6},{pooled_y} {x_map(pooled["effect"])},{pooled_y+6}" fill="#dc2626" />',
        ]
    )

    ticks = 6
    for idx in range(ticks + 1):
        value = min_x + ((max_x - min_x) * idx / ticks)
        x = x_map(value)
        lines.append(f'<line x1="{x}" y1="{height - 48}" x2="{x}" y2="{height - 42}" stroke="#334155" />')
        lines.append(f'<text x="{x - 12}" y="{height - 28}" font-size="10" font-family="Arial" fill="#334155">{value:.2f}</text>')

    lines.append("</svg>")
    return "".join(lines)


def funnel_plot_svg(effects_rows: List[Dict], pooled_effect: float) -> str:
    width, height = 520, 360
    left, right = 70, 480
    top, bottom = 40, 320
    min_x = min([row["effect"] for row in effects_rows] + [pooled_effect]) - 1.0
    max_x = max([row["effect"] for row in effects_rows] + [pooled_effect]) + 1.0
    max_se = max(row["standard_error"] for row in effects_rows) if effects_rows else 1.0

    def x_map(value: float) -> float:
        return left + ((value - min_x) / (max_x - min_x)) * (right - left) if max_x != min_x else (left + right) / 2

    def y_map(value: float) -> float:
        return top + ((value / max_se) * (bottom - top)) if max_se > 0 else top

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<text x="20" y="24" font-size="16" font-family="Arial" fill="#0f172a">Funnel Plot</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#334155" />',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#334155" />',
        f'<line x1="{x_map(pooled_effect)}" y1="{top}" x2="{x_map(pooled_effect)}" y2="{bottom}" stroke="#dc2626" stroke-dasharray="5 4" />',
    ]
    for row in effects_rows:
        lines.append(
            f'<circle cx="{x_map(row["effect"])}" cy="{y_map(row["standard_error"])}" r="3.2" fill="#2563eb" />'
        )
    lines.append("</svg>")
    return "".join(lines)

