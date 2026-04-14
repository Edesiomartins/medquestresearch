from __future__ import annotations

from typing import Dict, List

from backend.schemas.meta import PrismaCounts
from backend.schemas.studies import StudyExtraction


def build_prisma_counts(studies: List[StudyExtraction]) -> PrismaCounts:
    identified = len(studies)
    screened = identified
    included = len([item for item in studies if item.included])
    excluded = [item for item in studies if not item.included]
    eligible = included + len(excluded)
    reasons: List[Dict[str, str]] = []
    for row in excluded:
        reasons.append(
            {
                "study_id": row.study_id,
                "reason": row.exclusion_reason or "Excluído na revisão manual",
            }
        )
    return PrismaCounts(
        identified=identified,
        screened=screened,
        eligible=eligible,
        included=included,
        excluded_reasons=reasons,
    )

