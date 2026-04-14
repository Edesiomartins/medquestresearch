# Roteador de modelos por tipo de tarefa (OpenRouter apenas — base_url aponta para openrouter.ai).
# IDs podem mudar; ajuste via OPENROUTER_MODEL_* no ambiente.

# PDF / tradução de chunks (prioridade: Elephant no OpenRouter)
MODELOS_PDF = [
    "openrouter/elephant-alpha",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-nano-9b-v2:free",
]

MODELOS_EXTRACTION = [
    "openrouter/elephant-alpha",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-nano-9b-v2:free",
]

MODELOS_ANALYSIS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/elephant-alpha",
    "z-ai/glm-4.5-air:free",
]

MODELOS_WRITING = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/elephant-alpha",
    "z-ai/glm-4.5-air:free",
]

MODELOS_FALLBACK = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/elephant-alpha",
    "nvidia/nemotron-nano-9b-v2:free",
    "z-ai/glm-4.5-air:free",
]

# Mapeamento tipo de tarefa -> lista de modelos (ordem de preferência)
_TIPO_TO_LIST = {
    "pdf": MODELOS_PDF,
    "extracao": MODELOS_EXTRACTION,
    "prisma": MODELOS_ANALYSIS,
    "critica": MODELOS_ANALYSIS,
    "explicacao": MODELOS_ANALYSIS,
    "meta_analise": MODELOS_ANALYSIS,
    "redacao": MODELOS_WRITING,
    "geral": MODELOS_ANALYSIS,
}


def escolher_modelo(tipo: str) -> str:
    """Retorna o primeiro modelo da lista recomendada para o tipo. Compatibilidade com código que espera um único modelo."""
    lista = modelos_para_tipo(tipo)
    return lista[0] if lista else MODELOS_FALLBACK[0]


def modelos_para_tipo(tipo: str) -> list:
    """Retorna a lista de modelos recomendada para o tipo (extraction, analysis, writing)."""
    return list(_TIPO_TO_LIST.get(tipo, MODELOS_ANALYSIS))
