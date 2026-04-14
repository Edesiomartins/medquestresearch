from __future__ import annotations

import json
from typing import Dict

from backend.schemas.article import ArticleSections

try:
    from backend.gpt_engine import gerar_resposta
except Exception:
    from gpt_engine import gerar_resposta  # type: ignore


SECTION_PROMPTS: Dict[str, str] = {
    "abstract": "Escreva um resumo estruturado (objetivo, métodos, resultados, conclusão).",
    "introduction": "Escreva a introdução com lacuna de conhecimento e objetivo da revisão.",
    "methods": "Escreva métodos alinhados ao PRISMA com elegibilidade, busca, extração e síntese.",
    "results": "Escreva resultados com números da metanálise sem inventar valores.",
    "discussion": "Escreva discussão com heterogeneidade, vieses, limitações e implicações.",
    "conclusion": "Escreva conclusão objetiva baseada nos achados quantitativos.",
}


def _build_context(meta_result: Dict, section: str) -> str:
    payload = {
        "section": section,
        "question": meta_result.get("question"),
        "effect_measure": meta_result.get("effect_measure"),
        "model_used": meta_result.get("model_used"),
        "studies_included": [row.get("study_id") for row in meta_result.get("studies_included", [])],
        "pooled_result": meta_result.get("pooled_result"),
        "heterogeneity": meta_result.get("heterogeneity"),
        "publication_bias": meta_result.get("publication_bias"),
        "leave_one_out_top5": meta_result.get("leave_one_out", [])[:5],
        "subgroups": meta_result.get("subgroups", []),
        "prisma": meta_result.get("prisma"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def generate_article_sections(meta_result: Dict) -> ArticleSections:
    sections = {}
    for section, instruction in SECTION_PROMPTS.items():
        context = _build_context(meta_result, section)
        prompt = (
            "Você é um redator científico em epidemiologia clínica.\n"
            f"{instruction}\n"
            "Regras:\n"
            "- Use SOMENTE os números do JSON.\n"
            "- Se faltar dado, declare limitação explicitamente.\n"
            "- Não invente referências.\n\n"
            f"JSON:\n{context}"
        )
        sections[section] = gerar_resposta(
            prompt,
            temperatura=0.3,
            max_output_tokens=1600,
            tipo="redacao",
        )
    return ArticleSections(**sections)

