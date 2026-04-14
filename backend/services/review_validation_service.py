from __future__ import annotations

from typing import List, Tuple

from backend.schemas.studies import OutcomeExtraction, StudyExtraction


def _has_continuous_data(outcome: OutcomeExtraction) -> bool:
    return all(
        value is not None
        for value in [
            outcome.intervention_mean,
            outcome.intervention_sd,
            outcome.intervention_total,
            outcome.comparator_mean,
            outcome.comparator_sd,
            outcome.comparator_total,
        ]
    )


def _has_binary_data(outcome: OutcomeExtraction) -> bool:
    return all(
        value is not None
        for value in [
            outcome.intervention_events,
            outcome.intervention_total,
            outcome.comparator_events,
            outcome.comparator_total,
        ]
    )


def validate_reviewed_studies(studies: List[StudyExtraction]) -> Tuple[List[StudyExtraction], List[str]]:
    notes: List[str] = []
    normalized: List[StudyExtraction] = []

    for study in studies:
        valid_outcomes = 0
        for outcome in study.outcomes:
            if outcome.outcome_type == "continuous" and _has_continuous_data(outcome):
                valid_outcomes += 1
            elif outcome.outcome_type == "binary" and _has_binary_data(outcome):
                valid_outcomes += 1
            elif outcome.outcome_type == "generic":
                valid_outcomes += 1

        item = study.copy(deep=True)
        if item.included and valid_outcomes == 0:
            # Mantém a decisão do revisor humano; apenas sinaliza limitação quantitativa.
            notes.append(
                f"{item.study_id} está incluído, mas sem dados numéricos completos para pooling quantitativo."
            )
        elif not item.included and not item.exclusion_reason:
            item.exclusion_reason = "Excluído na revisão manual."
        normalized.append(item)

    if not notes:
        notes.append("Revisão validada sem inconsistências críticas.")
    return normalized, notes

