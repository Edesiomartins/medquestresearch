from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from backend.schemas.studies import OutcomeExtraction, StudyExtraction

try:
    from backend.gpt_engine import gerar_resposta_json
except Exception:
    try:
        from gpt_engine import gerar_resposta_json  # type: ignore
    except Exception:
        gerar_resposta_json = None  # type: ignore

logger = logging.getLogger(__name__)

TITLE_MARKER = "[[MEDQUEST_TITLE]]:"

# Limite de caracteres enviados ao LLM por artigo.
MAX_LLM_CHARS = 14000

EXTRACTION_PROMPT = """Você é um metodologista de revisões sistemáticas (Cochrane/PRISMA 2020).
Extraia do artigo científico abaixo os dados estruturados para metanálise.

Responda SOMENTE com JSON válido, exatamente neste formato:
{{
  "citation": "Primeiro autor, ano. Título abreviado",
  "title": "Título completo do artigo",
  "year": 2020,
  "country": "País do estudo ou null",
  "design": "RCT|cohort|case-control|cross-sectional|quasi-experimental|other",
  "sample_size": 120,
  "arms": ["nome do braço intervenção", "nome do braço controle"],
  "interventions": ["descrição da intervenção"],
  "comparators": ["descrição do comparador"],
  "follow_up": "duração do seguimento ou null",
  "outcomes": [
    {{
      "outcome_name": "nome do desfecho",
      "outcome_type": "continuous|binary",
      "timepoint": "momento da medida ou null",
      "intervention_mean": 12.3,
      "intervention_sd": 4.5,
      "intervention_events": null,
      "intervention_total": 60,
      "comparator_mean": 15.1,
      "comparator_sd": 5.0,
      "comparator_events": null,
      "comparator_total": 60,
      "evidence_snippet": "trecho literal do texto de onde os números foram extraídos",
      "confidence": "high|medium|low"
    }}
  ]
}}

Regras obrigatórias:
- Use SOMENTE números presentes no texto. NUNCA invente ou estime valores.
- Para desfechos contínuos preencha mean/sd/total dos dois grupos; deixe events como null.
- Para desfechos binários preencha events/total dos dois grupos; deixe mean/sd como null.
- Se um valor não estiver no texto, use null.
- Se o texto reportar erro padrão (SE) em vez de SD, converta: SD = SE * raiz(N) e marque confidence "medium".
- Se reportar mediana/IQR sem média/SD, deixe mean/sd null e marque confidence "low".
- Extraia no máximo 5 desfechos, priorizando o desfecho primário declarado.
- evidence_snippet deve ser uma cópia literal curta (<= 240 caracteres) do texto.

TEXTO DO ARTIGO:
{article_text}
"""


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


def _trim_text_for_llm(text: str, max_chars: int = MAX_LLM_CHARS) -> str:
    """Reduz o texto priorizando início (título/resumo/métodos) e seção de resultados."""
    if len(text) <= max_chars:
        return text
    head_budget = int(max_chars * 0.55)
    tail_budget = max_chars - head_budget
    head = text[:head_budget]

    # Tenta ancorar a segunda metade na seção de resultados.
    lowered = text.lower()
    anchor = -1
    for marker in ("\nresults", "\n3. results", "resultados"):
        anchor = lowered.find(marker, head_budget)
        if anchor != -1:
            break
    if anchor == -1:
        anchor = head_budget
    tail = text[anchor:anchor + tail_budget]
    return head + "\n[...trecho omitido...]\n" + tail


def _safe_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result or result in (float("inf"), float("-inf")):
        return None
    return result


def _safe_int(value: Any) -> Optional[int]:
    parsed = _safe_float(value)
    if parsed is None or parsed < 0:
        return None
    return int(round(parsed))


def _safe_str(value: Any, max_len: int = 320) -> Optional[str]:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_len] if text else None


def _safe_str_list(value: Any, max_items: int = 6) -> List[str]:
    if not isinstance(value, list):
        return []
    items = [_safe_str(item) for item in value[:max_items]]
    return [item for item in items if item]


def _coerce_outcome(raw: Dict[str, Any], outcome_id: str) -> Optional[OutcomeExtraction]:
    if not isinstance(raw, dict):
        return None
    name = _safe_str(raw.get("outcome_name"), 200)
    if not name:
        return None
    outcome_type = raw.get("outcome_type")
    if outcome_type not in {"continuous", "binary", "generic"}:
        outcome_type = "generic"

    snippet = _safe_str(raw.get("evidence_snippet"), 280)
    confidence = raw.get("confidence")
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    outcome = OutcomeExtraction(
        outcome_id=outcome_id,
        outcome_name=name,
        outcome_type=outcome_type,
        timepoint=_safe_str(raw.get("timepoint"), 120),
        intervention_mean=_safe_float(raw.get("intervention_mean")),
        intervention_sd=_safe_float(raw.get("intervention_sd")),
        intervention_events=_safe_int(raw.get("intervention_events")),
        intervention_total=_safe_int(raw.get("intervention_total")),
        comparator_mean=_safe_float(raw.get("comparator_mean")),
        comparator_sd=_safe_float(raw.get("comparator_sd")),
        comparator_events=_safe_int(raw.get("comparator_events")),
        comparator_total=_safe_int(raw.get("comparator_total")),
        evidence_snippets=[snippet] if snippet else [],
        page_hints=["not_reported"],
        confidence_flags={"extraction_confidence": confidence, "source": "llm"},
        needs_user_confirmation=True,
    )

    # Coerência básica: eventos não podem exceder o total do grupo.
    if (
        outcome.intervention_events is not None
        and outcome.intervention_total is not None
        and outcome.intervention_events > outcome.intervention_total
    ):
        outcome.intervention_events = None
        outcome.confidence_flags["intervention_events"] = "inconsistent_with_total"
    if (
        outcome.comparator_events is not None
        and outcome.comparator_total is not None
        and outcome.comparator_events > outcome.comparator_total
    ):
        outcome.comparator_events = None
        outcome.confidence_flags["comparator_events"] = "inconsistent_with_total"
    if outcome.intervention_sd is not None and outcome.intervention_sd < 0:
        outcome.intervention_sd = None
    if outcome.comparator_sd is not None and outcome.comparator_sd < 0:
        outcome.comparator_sd = None
    return outcome


def _coerce_study(raw: Dict[str, Any], study_id: str, fallback_citation: str) -> StudyExtraction:
    outcomes: List[OutcomeExtraction] = []
    for index, raw_outcome in enumerate((raw.get("outcomes") or [])[:5], start=1):
        outcome = _coerce_outcome(raw_outcome, f"{study_id}_outcome_{index}")
        if outcome:
            outcomes.append(outcome)

    citation = _safe_str(raw.get("citation"), 320) or _safe_str(raw.get("title"), 320) or fallback_citation
    year = _safe_int(raw.get("year"))
    if year is not None and not (1900 <= year <= 2100):
        year = None

    return StudyExtraction(
        study_id=study_id,
        citation=citation,
        year=year,
        country=_safe_str(raw.get("country"), 80),
        design=_safe_str(raw.get("design"), 60),
        sample_size=_safe_int(raw.get("sample_size")),
        arms=_safe_str_list(raw.get("arms")),
        interventions=_safe_str_list(raw.get("interventions")),
        comparators=_safe_str_list(raw.get("comparators")),
        follow_up=_safe_str(raw.get("follow_up"), 120),
        outcomes=outcomes,
        evidence_snippets=[],
        page_hints=["not_reported"],
        confidence_flags={"source": "llm"},
        needs_user_confirmation=True,
    )


def _heuristic_study(project_id: str, index: int, text: str, embedded_title: str) -> StudyExtraction:
    """Fallback sem LLM: identifica título/ano e cria desfecho vazio para preenchimento manual."""
    citation = _citation_from_text(text, f"Study {index}", embedded_title=embedded_title)
    outcome = OutcomeExtraction(
        outcome_id=f"{project_id}_study_{index}_outcome_1",
        outcome_name="Primary outcome",
        outcome_type="continuous",
        evidence_snippets=[text[:280]] if text else [],
        page_hints=["not_reported"],
        confidence_flags={"source": "heuristic"},
        needs_user_confirmation=True,
    )
    return StudyExtraction(
        study_id=f"{project_id}_study_{index}",
        citation=citation,
        year=_extract_year(text),
        outcomes=[outcome],
        evidence_snippets=[text[:280]] if text else [],
        page_hints=["not_reported"],
        confidence_flags={"source": "heuristic"},
        needs_user_confirmation=True,
    )


def extract_study_with_llm(project_id: str, index: int, text: str, embedded_title: str) -> StudyExtraction:
    if gerar_resposta_json is None:
        raise RuntimeError("Motor LLM indisponível.")
    prompt = EXTRACTION_PROMPT.format(article_text=_trim_text_for_llm(text))
    raw = gerar_resposta_json(prompt, temperatura=0.1, max_tokens=2500, tipo="json", timeout_s=120)
    if not isinstance(raw, dict):
        raise ValueError("Resposta de extração não é um objeto JSON.")
    study_id = f"{project_id}_study_{index}"
    fallback_citation = _citation_from_text(text, f"Study {index}", embedded_title=embedded_title)
    return _coerce_study(raw, study_id, fallback_citation)


def extract_studies_from_texts(
    project_id: str,
    texts: List[str],
    use_llm: bool = True,
    notes: Optional[List[str]] = None,
) -> List[StudyExtraction]:
    """Extrai dados estruturados de cada artigo. Tenta LLM; cai no heurístico por arquivo."""
    studies: List[StudyExtraction] = []
    for index, text in enumerate(texts, start=1):
        embedded_title, clean_text = _split_embedded_title(text or "")
        study: Optional[StudyExtraction] = None
        if use_llm and clean_text.strip():
            try:
                study = extract_study_with_llm(project_id, index, clean_text, embedded_title)
                poolable = sum(
                    1
                    for outcome in study.outcomes
                    if (outcome.intervention_total is not None and outcome.comparator_total is not None)
                )
                if notes is not None:
                    notes.append(
                        f"Artigo {index}: extração automática encontrou {len(study.outcomes)} desfecho(s), "
                        f"{poolable} com dados de grupo. Revise antes do pooling."
                    )
            except Exception as error:
                logger.warning("Extração LLM falhou para artigo %s: %s", index, error)
                if notes is not None:
                    notes.append(
                        f"Artigo {index}: extração automática indisponível ({type(error).__name__}); "
                        "preencha os dados manualmente na revisão."
                    )
        if study is None:
            study = _heuristic_study(project_id, index, clean_text, embedded_title)
        studies.append(study)
    return studies
