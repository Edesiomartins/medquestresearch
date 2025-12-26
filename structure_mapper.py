# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

def gerar_mapa_estrutura(texto_artigo: str) -> str:
    """
    Mapeia a estrutura lógica e organizacional de um texto de artigo científico.
    SEM chunking - chama o modelo uma única vez.
    """
    prompt = f"""
Você é um mapeador de estrutura de documentos. Analise o texto do artigo científico
e descreva sua estrutura lógica e organizacional.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Texto do artigo:
{texto_artigo}

Apresente o mapa da estrutura, incluindo:
- Seções principais (Introdução, Métodos, Resultados, Discussão, Conclusão, etc.).
- Subseções importantes.
- A relação lógica entre as seções.
- O fluxo de informações e argumentos.
"""
    resposta = gerar_resposta(prompt)
    return resposta
