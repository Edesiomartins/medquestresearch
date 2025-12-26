# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

def visualizar_estrutura(texto_artigo: str) -> str:
    """
    Gera uma descrição textual para visualização da estrutura de um artigo científico.
    SEM chunking - chama o modelo uma única vez.
    """
    prompt = f"""
Você é um visualizador de estrutura de documentos. Analise o texto do artigo científico
e crie uma descrição textual que possa ser usada para gerar uma representação visual
da sua estrutura. Pense em um fluxograma, mapa mental ou diagrama de blocos.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Texto do artigo:
{texto_artigo}

Descreva a estrutura visualmente, incluindo:
- Nodos principais (seções).
- Nodos secundários (subseções).
- Conexões entre os nodos (fluxo lógico, dependências).
- Uma breve descrição do conteúdo de cada nodo.
Use um formato que facilite a compreensão visual (ex: lista hierárquica, pseudocódigo de diagrama).
"""
    resposta = gerar_resposta(prompt)
    return resposta
