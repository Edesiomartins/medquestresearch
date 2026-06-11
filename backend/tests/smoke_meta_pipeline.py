"""Smoke test do pipeline de metanálise (sem LLM).

Roda na raiz do projeto:
    python -m backend.tests.smoke_meta_pipeline
"""
from __future__ import annotations

import math

from backend.schemas.meta import EffectMeasure, MetaAnalyzeRequest, MetaModel
from backend.schemas.studies import OutcomeExtraction, StudyExtraction
from backend.services.meta_pipeline_service import analyze_meta


def _continuous_study(idx: int, mean_t: float, mean_c: float, sd: float, n: int, design: str = "RCT") -> StudyExtraction:
    return StudyExtraction(
        study_id=f"s{idx}",
        citation=f"Autor {idx}, 2020",
        year=2020,
        design=design,
        outcomes=[
            OutcomeExtraction(
                outcome_id=f"s{idx}_o1",
                outcome_name="Dor (escala 0-10)",
                outcome_type="continuous",
                intervention_mean=mean_t,
                intervention_sd=sd,
                intervention_total=n,
                comparator_mean=mean_c,
                comparator_sd=sd,
                comparator_total=n,
            )
        ],
    )


def _binary_study(idx: int, ev_t: int, n_t: int, ev_c: int, n_c: int) -> StudyExtraction:
    return StudyExtraction(
        study_id=f"b{idx}",
        citation=f"Autor binário {idx}, 2021",
        year=2021,
        design="RCT",
        outcomes=[
            OutcomeExtraction(
                outcome_id=f"b{idx}_o1",
                outcome_name="Mortalidade",
                outcome_type="binary",
                intervention_events=ev_t,
                intervention_total=n_t,
                comparator_events=ev_c,
                comparator_total=n_c,
            )
        ],
    )


def test_smd_hedges() -> None:
    studies = [
        _continuous_study(1, 4.0, 6.0, 2.5, 30),
        _continuous_study(2, 4.5, 6.2, 2.8, 45),
        _continuous_study(3, 5.0, 5.9, 2.2, 25, design="cohort"),
    ]
    request = MetaAnalyzeRequest(
        question="Intervenção reduz dor?",
        effect_measure=EffectMeasure.smd,
        model_used=MetaModel.random_reml,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "success", result.warnings
    assert result.pooled_result is not None
    assert result.pooled_result.k == 3
    # Efeito negativo (intervenção reduz dor) e correção de Hedges aplicada.
    assert result.pooled_result.effect < 0
    row1 = result.effects_table[0]
    cohen_d = (4.0 - 6.0) / 2.5
    assert abs(row1.effect) < abs(cohen_d), "Hedges g deve encolher o d de Cohen"
    assert result.forest_plot_svg and result.forest_plot_svg.startswith("<svg")
    assert result.funnel_plot_svg and result.funnel_plot_svg.startswith("<svg")
    assert result.heterogeneity is not None
    print("OK SMD/Hedges:", f"g={result.pooled_result.effect:.3f} I2={result.heterogeneity.I2:.1f}%")


def test_md() -> None:
    studies = [
        _continuous_study(1, 4.0, 6.0, 2.5, 30),
        _continuous_study(2, 4.5, 6.2, 2.8, 45),
    ]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.md,
        model_used=MetaModel.fixed,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "success", result.warnings
    assert result.pooled_result is not None
    assert -2.5 < result.pooled_result.effect < -1.5, result.pooled_result.effect
    print("OK MD:", f"MD={result.pooled_result.effect:.3f}")


def test_rr_zero_cells_and_scale() -> None:
    studies = [
        _binary_study(1, 5, 100, 12, 100),
        _binary_study(2, 0, 80, 7, 80),      # célula zero -> correção de continuidade
        _binary_study(3, 8, 120, 15, 118),
        _binary_study(4, 0, 50, 0, 50),      # duplo-zero -> deve ser excluído com warning
    ]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.log_rr,
        model_used=MetaModel.random_dl,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "success", result.warnings
    assert result.pooled_result is not None
    assert result.pooled_result.k == 3, f"duplo-zero deveria sair do pooling (k={result.pooled_result.k})"
    assert any("não é informativo" in w for w in result.warnings), result.warnings
    # Escala natural: RR > 0, protetor < 1, e tabela coerente com o pooled.
    assert 0 < result.pooled_result.effect < 1
    for row in result.effects_table:
        assert row.effect > 0, "tabela deve estar em escala natural (RR)"
        assert row.ci_low < row.effect < row.ci_high
    for loo in result.leave_one_out:
        assert loo.pooled_effect > 0, "leave-one-out deve estar em escala natural"
    print("OK RR:", f"RR={result.pooled_result.effect:.3f} k={result.pooled_result.k}")


def test_or_basic() -> None:
    studies = [
        _binary_study(1, 5, 100, 12, 100),
        _binary_study(2, 9, 90, 14, 95),
    ]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.log_or,
        model_used=MetaModel.random_pm,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "success", result.warnings
    assert result.pooled_result is not None and result.pooled_result.effect > 0
    print("OK OR:", f"OR={result.pooled_result.effect:.3f}")


def test_double_counting_guard() -> None:
    study = _continuous_study(1, 4.0, 6.0, 2.5, 30)
    extra = OutcomeExtraction(
        outcome_id="s1_o2",
        outcome_name="Dor em 6 meses",
        outcome_type="continuous",
        intervention_mean=4.2,
        intervention_sd=2.4,
        intervention_total=30,
        comparator_mean=5.8,
        comparator_sd=2.6,
        comparator_total=30,
    )
    study.outcomes.append(extra)
    studies = [study, _continuous_study(2, 4.5, 6.2, 2.8, 45)]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.smd,
        model_used=MetaModel.fixed,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.pooled_result is not None and result.pooled_result.k == 2
    assert any("dupla contagem" in w for w in result.warnings), result.warnings
    print("OK dupla contagem:", result.warnings[0][:80])


def test_insufficient_data() -> None:
    studies = [_continuous_study(1, 4.0, 6.0, 2.5, 30)]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.smd,
        model_used=MetaModel.fixed,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "warning"
    assert result.pooled_result is None
    print("OK dados insuficientes -> síntese narrativa")


def test_wrong_measure_for_data() -> None:
    # Dados contínuos com medida binária: todos saem do pooling com warnings nominais.
    studies = [
        _continuous_study(1, 4.0, 6.0, 2.5, 30),
        _continuous_study(2, 4.5, 6.2, 2.8, 45),
    ]
    request = MetaAnalyzeRequest(
        question="",
        effect_measure=EffectMeasure.log_rr,
        model_used=MetaModel.fixed,
        studies=studies,
    )
    result = analyze_meta(request)
    assert result.status == "warning"
    assert any("excluído do pooling" in w for w in result.warnings), result.warnings
    print("OK medida incompatível -> warnings nominais")


if __name__ == "__main__":
    test_smd_hedges()
    test_md()
    test_rr_zero_cells_and_scale()
    test_or_basic()
    test_double_counting_guard()
    test_insufficient_data()
    test_wrong_measure_for_data()
    print("\nTodos os smoke tests passaram.")
