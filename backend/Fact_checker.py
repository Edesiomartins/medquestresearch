# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

def verificar_fatos(texto_artigo: str, afirmacoes_para_verificar: str = "") -> str:
    """
    Verifica fatos em um texto de artigo científico.
    SEM chunking - chama o modelo uma única vez.
    """
    prompt = f"""
Você é um verificador de fatos especializado em ciência. Analise o texto do artigo
e verifique a veracidade das informações, especialmente as relacionadas a: {afirmacoes_para_verificar}.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Texto do artigo:
{texto_artigo}

Para cada afirmação relevante ou para as especificadas, indique:
- Se é verdadeira, falsa ou não verificável com as informações fornecidas.
- A evidência ou raciocínio que suporta sua conclusão.
- Se possível, a fonte dentro do próprio texto.
"""
    resposta = gerar_resposta(prompt)
    return resposta
