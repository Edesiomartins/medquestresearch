# Roteador de modelos por tipo de tarefa (OpenRouter).
# Cada tarefa usa o modelo mais adequado; fallback em gpt_engine.

MODEL_ROUTER = {
    "extracao": "openai/gpt-oss-20b:free",
    "prisma": "meta-llama/llama-3.3-70b-instruct:free",
    "critica": "meta-llama/llama-3.3-70b-instruct:free",
    "explicacao": "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta_analise": "meta-llama/llama-3.3-70b-instruct:free",
    "geral": "meta-llama/llama-3.3-70b-instruct:free",
}

MODELOS_FALLBACK = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]


def escolher_modelo(tipo: str) -> str:
    """Retorna o modelo recomendado para o tipo de tarefa. Padrão: geral."""
    return MODEL_ROUTER.get(tipo, MODEL_ROUTER["geral"])
