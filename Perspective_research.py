from gpt_engine import gerar_resposta

def buscar_perspectivas_pubmed(texto_artigo):
    prompt = f"""
Você é um assistente científico que ajuda pesquisadores a analisar múltiplas perspectivas sobre um tema.

Abaixo está o conteúdo principal de um artigo científico. Leia atentamente e:

1. Identifique o tema central e a hipótese principal do artigo.
2. Pesquise no PubMed estudos recentes que:
   - Confirmem a mesma hipótese
   - Apresentem conclusões diferentes ou contraditórias
3. Compare os achados do artigo com os estudos encontrados.
4. Apresente um resumo estruturado com perspectivas distintas (com autores e datas se possível).

Texto base:
\"\"\"
{texto_artigo}
\"\"\"

Publique as conclusões em forma de comparação.
"""
    resposta = gerar_resposta(prompt)
    return resposta
