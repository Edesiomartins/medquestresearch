from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

# matplotlib é opcional; se não estiver instalado, ainda calculamos todos os números
try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:
    plt = None


@dataclass
class Effect:
    study_id: str
    label: str
    yi: float          # estimativa de efeito (log OR/RR em escala log; SMD já linear)
    vi: float          # variância
    ci_low: float
    ci_high: float
    weight_fixed: float = 0.0
    weight_random: float = 0.0


def _norm_ci(yi: float, vi: float) -> Tuple[float, float]:
    se = math.sqrt(vi)
    return yi - 1.96 * se, yi + 1.96 * se


# -----------------------------
# Effect size builders
# -----------------------------

def effect_smd_hedges_g(
    study_id: str,
    label: str,
    n_t: int, mean_t: float, sd_t: float,
    n_c: int, mean_c: float, sd_c: float,
) -> Effect:
    """
    Hedges g (SMD) com correção de amostra pequena (J).
    """
    if min(n_t, n_c) <= 1:
        raise ValueError("n_t e n_c precisam ser > 1 para SMD.")

    sp2 = (((n_t - 1) * (sd_t ** 2)) + ((n_c - 1) * (sd_c ** 2))) / (n_t + n_c - 2)
    if sp2 <= 0:
        raise ValueError("Variância pooled inválida para SMD (sp2 <= 0).")

    sp = math.sqrt(sp2)
    d = (mean_t - mean_c) / sp

    df = n_t + n_c - 2
    J = 1 - (3 / (4 * df - 1)) if df > 1 else 1.0
    g = J * d

    vi = (n_t + n_c) / (n_t * n_c) + (g ** 2) / (2 * (n_t + n_c - 2))
    ci_low, ci_high = _norm_ci(g, vi)
    return Effect(study_id=study_id, label=label, yi=g, vi=vi, ci_low=ci_low, ci_high=ci_high)


def effect_log_rr(
    study_id: str,
    label: str,
    e_t: int, n_t: int,
    e_c: int, n_c: int,
    continuity: float = 0.5
) -> Effect:
    """
    log(RR) com correção de continuidade opcional para células zero.
    """
    if min(n_t, n_c) <= 0:
        raise ValueError("n_t e n_c precisam ser > 0.")
    if e_t < 0 or e_c < 0:
        raise ValueError("Eventos não podem ser negativos.")
    if e_t > n_t or e_c > n_c:
        raise ValueError("Eventos não podem exceder N.")

    a, b = e_t, n_t - e_t
    c, d = e_c, n_c - e_c

    if min(a, b, c, d) == 0:
        a += continuity
        b += continuity
        c += continuity
        d += continuity

    risk_t = a / (a + b)
    risk_c = c / (c + d)
    if risk_t <= 0 or risk_c <= 0:
        raise ValueError("Riscos inválidos para RR (<= 0).")

    yi = math.log(risk_t / risk_c)
    vi = (1 / a) - (1 / (a + b)) + (1 / c) - (1 / (c + d))
    ci_low, ci_high = _norm_ci(yi, vi)
    return Effect(study_id=study_id, label=label, yi=yi, vi=vi, ci_low=ci_low, ci_high=ci_high)


def effect_log_or(
    study_id: str,
    label: str,
    e_t: int, n_t: int,
    e_c: int, n_c: int,
    continuity: float = 0.5
) -> Effect:
    """
    log(OR) para desfechos binários 2x2, com correção de continuidade se necessário.
    """
    if min(n_t, n_c) <= 0:
        raise ValueError("n_t e n_c precisam ser > 0.")
    if e_t < 0 or e_c < 0:
        raise ValueError("Eventos não podem ser negativos.")
    if e_t > n_t or e_c > n_c:
        raise ValueError("Eventos não podem exceder N.")

    a, b = e_t, n_t - e_t
    c, d = e_c, n_c - e_c

    if min(a, b, c, d) == 0:
        a += continuity
        b += continuity
        c += continuity
        d += continuity

    yi = math.log((a * d) / (b * c))
    vi = (1 / a) + (1 / b) + (1 / c) + (1 / d)
    ci_low, ci_high = _norm_ci(yi, vi)
    return Effect(study_id=study_id, label=label, yi=yi, vi=vi, ci_low=ci_low, ci_high=ci_high)


# -----------------------------
# Pooling models
# -----------------------------

def _fixed_pool(effects: List[Effect]) -> Dict[str, Any]:
    for ef in effects:
        ef.weight_fixed = 1.0 / ef.vi

    w = sum(ef.weight_fixed for ef in effects)
    mu = sum(ef.weight_fixed * ef.yi for ef in effects) / w
    var_mu = 1.0 / w
    ci_low, ci_high = _norm_ci(mu, var_mu)

    Q = sum(ef.weight_fixed * (ef.yi - mu) ** 2 for ef in effects)
    df = max(len(effects) - 1, 0)
    I2 = 0.0
    if Q > 0 and df > 0:
        I2 = max(0.0, (Q - df) / Q) * 100.0

    return {
        "model": "fixed",
        "k": len(effects),
        "mu": mu,
        "var": var_mu,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "Q": Q,
        "df": df,
        "I2": I2,
        "tau2": 0.0,
    }


def _random_dl_pool(effects: List[Effect]) -> Dict[str, Any]:
    fixed = _fixed_pool(effects)
    Q = fixed["Q"]
    df = fixed["df"]

    w = [1.0 / ef.vi for ef in effects]
    sum_w = sum(w)
    sum_w2 = sum(x * x for x in w)
    C = sum_w - (sum_w2 / sum_w) if sum_w > 0 else 0.0
    tau2 = max(0.0, (Q - df) / C) if C > 0 and df > 0 else 0.0

    for ef in effects:
        ef.weight_random = 1.0 / (ef.vi + tau2)

    w_star = sum(ef.weight_random for ef in effects)
    mu = sum(ef.weight_random * ef.yi for ef in effects) / w_star if w_star > 0 else float("nan")
    var_mu = 1.0 / w_star if w_star > 0 else float("nan")
    ci_low, ci_high = _norm_ci(mu, var_mu)

    I2 = fixed["I2"]
    return {
        "model": "random_DL",
        "k": len(effects),
        "mu": mu,
        "var": var_mu,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "Q": Q,
        "df": df,
        "I2": I2,
        "tau2": tau2,
    }


def pool_effects(
    effects: List[Effect],
    model: str = "random_DL"
) -> Dict[str, Any]:
    if len(effects) == 0:
        raise ValueError("Lista de efeitos vazia.")
    if any(ef.vi <= 0 for ef in effects):
        raise ValueError("Variâncias devem ser > 0.")

    if model == "fixed":
        pooled = _fixed_pool(effects)
    else:
        pooled = _random_dl_pool(effects)

    return {
        "pooled": pooled,
        "effects": [ef.__dict__ for ef in effects],
    }


# -----------------------------
# Forest plot
# -----------------------------

def forest_plot_png(
    pooled: Dict[str, Any],
    effects: List[Effect],
    out_path: str,
    scale: str = "identity"
) -> Dict[str, Any]:
    """
    scale:
      - "identity": SMD etc (plota yi diretamente)
      - "exp": para log(OR/RR) (plota exp(yi))
    """
    if plt is None:
        return {"ok": False, "error": "matplotlib_not_available"}

    def _tr(x: float) -> float:
        return math.exp(x) if scale == "exp" else x

    ys = [_tr(ef.yi) for ef in effects]
    lows = [_tr(ef.ci_low) for ef in effects]
    highs = [_tr(ef.ci_high) for ef in effects]

    pooled_mu = _tr(pooled["mu"])
    pooled_low = _tr(pooled["ci_low"])
    pooled_high = _tr(pooled["ci_high"])

    y_pos = list(range(len(effects), 0, -1))

    plt.figure()
    for i, ef in enumerate(effects):
        plt.plot([lows[i], highs[i]], [y_pos[i], y_pos[i]])
        plt.plot([ys[i]], [y_pos[i]], marker="s")

    plt.plot([pooled_low, pooled_high], [0, 0])
    plt.plot([pooled_mu], [0], marker="D")

    plt.yticks([0] + y_pos, ["Pooled"] + [ef.label for ef in effects])
    plt.axvline(1.0 if scale == "exp" else 0.0, linestyle="--")
    plt.title("Forest plot")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()

    return {"ok": True, "path": out_path}

