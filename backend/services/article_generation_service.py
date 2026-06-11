from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

from backend.schemas.article import ArticleSections

try:
    from backend.gpt_engine import gerar_resposta
except Exception:
    try:
        from gpt_engine import gerar_resposta  # type: ignore
    except Exception:
        gerar_resposta = None  # type: ignore

logger = logging.getLogger(__name__)

SECTION_PROMPTS: Dict[str, str] = {
    "abstract": (
        "Escreva um RESUMO ESTRUTURADO conforme PRISMA 2020 com: objetivo, critérios de "
        "elegibilidade, métodos de síntese, resultados principais (com números), limitações e "
        "conclusão. Máximo 350 palavras."
    ),
    "introduction": (
        "Escreva a INTRODUÇÃO: contexto do problema clínico, o que já se sabe, a lacuna de "
        "conhecimento e o objetivo/pergunta da revisão. Prosa fluente, sem bullet points."
    ),
    "methods": (
        "Escreva a seção de MÉTODOS alinhada ao PRISMA 2020: critérios de elegibilidade, "
        "processo de seleção e extração com revisão humana, medida de efeito, modelo estatístico "
        "utilizado, avaliação de heterogeneidade (Q, I², tau²), análise de sensibilidade "
        "(leave-one-out), subgrupos e avaliação de viés de publicação (Egger/Begg)."
    ),
    "results": (
        "Escreva a seção de RESULTADOS: fluxo de seleção (números PRISMA), características dos "
        "estudos incluídos, efeito combinado com IC95% e p-valor, heterogeneidade (I², tau², p), "
        "análises de sensibilidade e subgrupos, e viés de publicação. Use os valores numéricos do JSON."
    ),
    "discussion": (
        "Escreva a DISCUSSÃO: síntese dos achados principais, interpretação da heterogeneidade, "
        "limitações (incluindo viés de publicação e qualidade da extração), implicações clínicas "
        "e para pesquisa futura. Prosa fluente, sem bullet points."
    ),
    "conclusion": (
        "Escreva a CONCLUSÃO objetiva e proporcional à força dos achados quantitativos, "
        "sem extrapolar além dos dados."
    ),
}

VALID_SECTIONS = set(SECTION_PROMPTS)


def _build_context(meta_result: Dict) -> str:
    studies_summary = []
    for row in meta_result.get("studies_included", []):
        studies_summary.append(
            {
                "citation": row.get("citation"),
                "year": row.get("year"),
                "country": row.get("country"),
                "design": row.get("design"),
                "sample_size": row.get("sample_size"),
                "interventions": row.get("interventions"),
                "comparators": row.get("comparators"),
                "follow_up": row.get("follow_up"),
            }
        )
    effects_table = [
        {
            "citation": row.get("citation"),
            "effect": row.get("effect"),
            "ci_low": row.get("ci_low"),
            "ci_high": row.get("ci_high"),
            "weight_random": row.get("weight_random"),
        }
        for row in meta_result.get("effects_table", [])
    ]
    payload = {
        "question": meta_result.get("question"),
        "effect_measure": meta_result.get("effect_measure"),
        "model_used": meta_result.get("model_used"),
        "studies_included": studies_summary,
        "excluded_reasons": (meta_result.get("prisma") or {}).get("excluded_reasons"),
        "effects_table": effects_table,
        "pooled_result": meta_result.get("pooled_result"),
        "heterogeneity": meta_result.get("heterogeneity"),
        "publication_bias": meta_result.get("publication_bias"),
        "leave_one_out_top5": meta_result.get("leave_one_out", [])[:5],
        "subgroups": meta_result.get("subgroups", []),
        "prisma": meta_result.get("prisma"),
        "narrative_results": meta_result.get("narrative_results"),
        "warnings": meta_result.get("warnings", []),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def _build_prompt(context: str, section: str, language: str = "pt") -> str:
    instruction = SECTION_PROMPTS[section]
    language_label = "português científico brasileiro" if language == "pt" else "scientific English"
    return (
        "Você é um redator científico sênior em epidemiologia clínica e revisões sistemáticas.\n"
        f"{instruction}\n"
        f"Idioma: {language_label}.\n"
        "Regras:\n"
        "- Use SOMENTE os números e estudos presentes no JSON; nunca invente valores ou referências.\n"
        "- Cite os estudos pelo campo 'citation' (autor, ano).\n"
        "- Se algum dado estiver ausente no JSON, declare a limitação explicitamente.\n"
        "- Não inclua título de seção nem markdown de cabeçalho; apenas o texto da seção.\n\n"
        f"JSON:\n{context}"
    )


def generate_article_section(meta_result: Dict, section: str, language: str = "pt") -> Optional[str]:
    """Gera apenas a seção pedida (1 chamada de LLM)."""
    if section not in VALID_SECTIONS:
        return None
    if gerar_resposta is None:
        raise RuntimeError("Motor LLM indisponível.")
    context = _build_context(meta_result)
    prompt = _build_prompt(context, section, language=language)
    return gerar_resposta(
        prompt,
        temperatura=0.3,
        max_output_tokens=1600,
        tipo="redacao",
    )


def generate_article_sections(meta_result: Dict, language: str = "pt") -> ArticleSections:
    """Gera todas as seções em paralelo (limite de 3 chamadas simultâneas)."""
    context = _build_context(meta_result)

    def _generate(section: str) -> tuple[str, Optional[str]]:
        try:
            text = gerar_resposta(
                _build_prompt(context, section, language=language),
                temperatura=0.3,
                max_output_tokens=1600,
                tipo="redacao",
            )
            return section, text
        except Exception as error:
            logger.warning("Falha ao gerar seção %s: %s", section, error)
            return section, f"[Seção não gerada automaticamente: {type(error).__name__}. Tente novamente.]"

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = dict(executor.map(_generate, SECTION_PROMPTS.keys()))
    return ArticleSections(**results)
