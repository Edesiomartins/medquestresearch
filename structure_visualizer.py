from gpt_engine import gerar_resposta

def gerar_mapa_visual(texto_artigo):
    prompt = f"""
Você é um assistente de leitura científica. Abaixo está o conteúdo principal de um artigo científico.

Crie uma visualização lógica da estrutura do artigo no formato de mapa mental textual. O mapa deve conter:

- Tema central no topo
- Tópicos principais como ramos
- Subtópicos e evidências como sub-ramos
- Use marcadores, setas ou recuos para simular o visual de um mapa

Texto do artigo:
{texto_artigo}

Formato de saída esperado:
Tema Central
├── Tópico 1
│   ├── Subtópico A
│   └── Subtópico B
├── Tópico 2
│   ├── Subtópico C
│   └── Subtópico D
...
"""

    resposta = gerar_resposta(prompt)
    return resposta
