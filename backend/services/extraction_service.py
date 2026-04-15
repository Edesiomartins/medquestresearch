from __future__ import annotations

import re
from typing import List

from backend.schemas.studies import OutcomeExtraction, StudyExtraction

TITLE_MARKER = "[[MEDQUEST_TITLE]]:"


def _split_embedded_title(text: str) -> tuple[str, str]:
    if not text:
        return "", ""
    pattern = rf"{re.escape(TITLE_MARKER)}\s*(.+?)(?:\n|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return "", text
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    clean_text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    return title, clean_text


def _is_likely_section_header(line: str) -> bool:
    normalized = (line or "").strip().lower().rstrip(":")
    return normalized in {
        "abstract",
        "introduction",
        "background",
        "methods",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "keywords",
    }


def _is_likely_author_line(line: str) -> bool:
    text = (line or "").strip()
    if not text:
        return False
    if "@" in text:
        return True
    comma_count = text.count(",")
    if comma_count >= 3 and len(text.split()) <= 20:
        return True
    return False


def _citation_from_text(text: str, fallback: str, embedded_title: str = "") -> str:
    if embedded_title and len(embedded_title) >= 12:
        return embedded_title[:320]

    if not text:
        return fallback

    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines:
        return fallback

    # Busca nas primeiras linhas por um candidato robusto a título.
    for line in lines[:20]:
        if len(line) < 12:
            continue
        if _is_likely_section_header(line):
            continue
        if _is_likely_author_line(line):
            continue
        if re.fullmatch(r"[0-9\W_]+", line):
            continue
        return line[:320]

    return lines[0][:320]


def _extract_year(text: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", text or "")
    return int(match.group(0)) if match else None


def extract_studies_from_texts(project_id: str, texts: List[str]) -> List[StudyExtraction]:
    studies: List[StudyExtraction] = []
    for index, text in enumerate(texts, start=1):
        embedded_title, clean_text = _split_embedded_title(text or "")
        citation = _citation_from_text(clean_text, f"Study {index}", embedded_title=embedded_title)
        year = _extract_year(clean_text)
        outcome = OutcomeExtraction(
            outcome_id=f"{project_id}_outcome_{index}",
            outcome_name="Primary outcome",
            outcome_type="continuous",
            evidence_snippets=[clean_text[:280]],
            page_hints=["not_reported"],
            needs_user_confirmation=True,
        )
        studies.append(
            StudyExtraction(
                study_id=f"{project_id}_study_{index}",
                citation=citation,
                year=year,
                outcomes=[outcome],
                evidence_snippets=[clean_text[:280]],
                page_hints=["not_reported"],
                needs_user_confirmation=True,
            )
        )
    return studies

