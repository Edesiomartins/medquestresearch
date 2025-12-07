from gpt_engine import gerar_resposta

def verificar_fatos(texto_artigo):
    prompt = f"""
Você é um especialista em revisão científica. Sua tarefa é verificar a precisão factual e a consistência científica no seguinte texto:

---
Texto do artigo:
{texto_artigo}

Analise e responda com:
- Afirmações potencialmente incorretas ou enganosas
- Pontos sem embasamento claro ou com lacunas de evidência
- Referências científicas desatualizadas ou problemáticas
- Possíveis correções ou observações críticas

Apresente o resultado de forma clara e estruturada, como uma lista crítica de verificação.
"""
    resposta = gerar_resposta(prompt)
    return resposta
