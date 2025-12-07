import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega chave do .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Verifica se a chave foi carregada
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Cria cliente OpenAI com a chave
client = OpenAI(api_key=api_key)

# Função para gerar resposta do GPT-4o
def gerar_resposta(prompt, temperatura=0.4):
    """
    Gera uma resposta usando o GPT-4o através da API OpenAI v1.0.0+
    
    Args:
        prompt: A pergunta ou texto do usuário
        temperatura: Controla a aleatoriedade (0.0 a 2.0), padrão 0.4
    
    Returns:
        str: A resposta gerada pelo modelo
    """
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em pesquisa científica e questões médicas."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperatura,
        )
        return resposta.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao gerar resposta: {str(e)}")
