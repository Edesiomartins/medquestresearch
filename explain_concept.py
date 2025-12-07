from gpt_engine import gerar_resposta

def explicar_conceito(texto_artigo, trecho_ou_termo, nivel="graduação"):
    prompt = f"""
Você é um assistente educacional. Um usuário está lendo um artigo científico e encontrou dificuldade para entender um conceito ou trecho específico.

---
Texto do artigo:
{texto_artigo}

Trecho ou termo a ser explicado:
"{trecho_ou_termo}"

Explique esse conteúdo como se estivesse ensinando para alguém com o seguinte nível de conhecimento: {nivel}.
Use uma linguagem clara, exemplos se necessário e evite jargões técnicos excessivos.
"""
    
    resposta = gerar_resposta(prompt)
    return resposta
