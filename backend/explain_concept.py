# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
    from .chunker import estimate_tokens
except ImportError:
    try:
        from gpt_engine import gerar_resposta
        from chunker import estimate_tokens
    except ImportError:
        import backend.gpt_engine as gpt_engine
        import backend.chunker as chunker
        gerar_resposta = gpt_engine.gerar_resposta
        estimate_tokens = chunker.estimate_tokens

def explicar_conceito(texto_artigo, trecho_ou_termo, nivel="graduação"):
    """
    Explica conceito usando chunking se texto for muito longo.
    """
    tokens = estimate_tokens(texto_artigo)
    
    # Se texto < 3000 tokens, processa normal
    if tokens < 3000:
        prompt = f"""
Você é um assistente educacional. Um usuário está lendo um artigo científico e encontrou dificuldade para entender um conceito ou trecho específico.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Texto do artigo:
{texto_artigo}

Trecho ou termo a ser explicado:
"{trecho_ou_termo}"

Explique esse conteúdo como se estivesse ensinando para alguém com o seguinte nível de conhecimento: {nivel}.
Use uma linguagem clara, exemplos se necessário e evite jargões técnicos excessivos.
"""
        resposta = gerar_resposta(prompt)
    
    # Se texto >= 3000 tokens, usa chunking
    else:
        try:
            from .chunker import chunk_text, combine_responses
        except ImportError:
            try:
                from chunker import chunk_text, combine_responses
            except ImportError:
                import backend.chunker as chunker
                chunk_text = chunker.chunk_text
                combine_responses = chunker.combine_responses
        chunks = chunk_text(texto_artigo, chunk_size=3000, overlap=500)
        respostas = []
        
        for chunk in chunks:
            prompt = f"""
Você é um assistente educacional analisando um trecho de artigo científico.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

---
Trecho do artigo:
{chunk}

Termo/conceito a explicar: "{trecho_ou_termo}"

Explique como se estivesse ensinando para alguém com nível: {nivel}.
Use linguagem clara, exemplos se necessário, evite jargões excessivos.
"""
            resposta = gerar_resposta(prompt)
            respostas.append(resposta)
        
        resposta = combine_responses(respostas)
    
    return resposta
