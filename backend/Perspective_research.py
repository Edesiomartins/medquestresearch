# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

def buscar_perspectivas_pubmed(texto_artigo: str, tema_foco: str = "") -> str:
    """
    Identifica diferentes perspectivas ou pontos de vista em um texto de artigo científico.
    NOTA: Esta função é chamada dentro de run_with_two_chunks, então não faz chunking adicional.
    """
    # Limitar texto para evitar chamadas muito longas
    texto_artigo = texto_artigo[:4000]
    
    prompt = f"""
Você é um pesquisador de perspectivas. Analise o texto do artigo científico
e identifique as diferentes perspectivas, argumentos ou pontos de vista apresentados,
especialmente em relação a: {tema_foco}.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Texto do artigo:
{texto_artigo}

Apresente as perspectivas encontradas, indicando:
- Qual é a perspectiva.
- Quem a defende (se identificável).
- Os principais argumentos ou evidências que a sustentam.
- Se há perspectivas conflitantes ou complementares.
"""
    resposta = gerar_resposta(prompt)
    return resposta
