from __future__ import annotations

from typing import List

try:
    from backend.gpt_engine import gerar_resposta_com_modelos_preferenciais
except Exception:
    from gpt_engine import gerar_resposta_com_modelos_preferenciais  # type: ignore


TRANSLATION_PRIMARY_MODEL = "openrouter/elephant-alpha"
TRANSLATION_FALLBACK_MODEL = "openai/gpt-oss-120b:free"
TRANSLATION_MODELS: List[str] = [TRANSLATION_PRIMARY_MODEL, TRANSLATION_FALLBACK_MODEL]


def _build_translation_prompt(text: str) -> str:
    return (
        "Traduza o texto abaixo para português brasileiro com qualidade editorial para literatura em saúde.\n"
        "Regras obrigatórias:\n"
        "- Preserve integralmente números, p-valores, IC95%, unidades e nomes de escalas.\n"
        "- Não resuma, não omita e não adicione conteúdo.\n"
        "- Mantenha terminologia biomédica técnica consistente.\n"
        "- Preserve quebras de parágrafo.\n"
        "- Retorne apenas a tradução.\n\n"
        f"Texto:\n{text}"
    )


def translate_to_pt_br_health_literature(text: str, chunk_size: int = 2200) -> str:
    if not text or not text.strip():
        return text

    chunks: List[str] = []
    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        if not chunk.strip():
            continue
        translated = gerar_resposta_com_modelos_preferenciais(
            prompt=_build_translation_prompt(chunk),
            preferred_models=TRANSLATION_MODELS,
            temperatura=0.1,
            max_output_tokens=1600,
            timeout_s=90,
        )
        chunks.append(translated)
    return "\n\n".join(chunks) if chunks else text

