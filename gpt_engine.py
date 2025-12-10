import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega chave do .env
load_dotenv()
api_key = os.getenv("API_OPENAI_KEY_RESEARCH")

# Verifica se a chave foi carregada
if not api_key:
    raise ValueError("API_OPENAI_KEY_RESEARCH não encontrada no WSGI")

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


def resumir_chunks(chunks, max_tokens=1000):
    """
    Resume lista de chunks para reduzir tamanho (para PDFs longos).
    Args: chunks (lista strings), max_tokens (limite por resumo).
    Returns: String resumida única.
    """
    resumos = []
    for i, chunk in enumerate(chunks):
        prompt = f"""
        Resuma este chunk de artigo científico de forma concisa, mantendo conceitos chave, métodos e conclusões.
        Foque em {max_tokens} tokens. Chunk {i+1}/{len(chunks)}:

        {chunk}

        """
        resumo = gerar_resposta(prompt, temperatura=0.2)  # Baixa temp para precisão
        resumos.append(resumo)
    
    # Combinar resumos
    prompt_final = f"Combine estes resumos de chunks em um texto coeso final:\n" + "\n\n".join(resumos)
    texto_final = gerar_resposta(prompt_final, temperatura=0.3)
    
    return texto_final