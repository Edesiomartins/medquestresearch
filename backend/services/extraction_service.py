from __future__ import annotations

import re
from typing import List

from backend.schemas.studies import OutcomeExtraction, StudyExtraction


def _citation_from_text(text: str, fallback: str) -> str:
    first_line = (text or "").strip().splitlines()[0] if text else ""
    return first_line[:220] if first_line else fallback


def _extract_year(text: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", text or "")
    return int(match.group(0)) if match else None


def extract_studies_from_texts(project_id: str, texts: List[str]) -> List[StudyExtraction]:
    studies: List[StudyExtraction] = []
    for index, text in enumerate(texts, start=1):
        citation = _citation_from_text(text, f"Study {index}")
        year = _extract_year(text)
        outcome = OutcomeExtraction(
            outcome_id=f"{project_id}_outcome_{index}",
            outcome_name="Primary outcome",
            outcome_type="continuous",
            evidence_snippets=[(text or "")[:280]],
            page_hints=["not_reported"],
            needs_user_confirmation=True,
        )
        studies.append(
            StudyExtraction(
                study_id=f"{project_id}_study_{index}",
                citation=citation,
                year=year,
                outcomes=[outcome],
                evidence_snippets=[(text or "")[:280]],
                page_hints=["not_reported"],
                needs_user_confirmation=True,
            )
        )
    return studies

