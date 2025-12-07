from gpt_engine import gerar_resposta

def gerar_mapa_estrutura(texto_artigo):
    prompt = f"""
Você é um assistente de leitura científica. Abaixo está o texto de um artigo científico.
Sua tarefa é analisar a estrutura lógica e gerar um mapa mental textual com os seguintes elementos:

- Principais seções (introdução, métodos, resultados, discussão, conclusão)
- Conexão entre as ideias
- Destaques conceituais

Apresente o resultado de forma organizada e hierárquica, usando marcadores, recuos e tópicos, como um esboço visual.

Texto do artigo:
{texto_artigo}
"""
    resposta = gerar_resposta(prompt)
    return resposta
