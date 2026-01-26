import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Tentar importação relativa primeiro, depois absoluta
try:
    from .chunker import chunk_text, combine_responses, estimate_tokens
except ImportError:
    try:
        from chunker import chunk_text, combine_responses, estimate_tokens
    except ImportError:
        import backend.chunker as chunker
        chunk_text = chunker.chunk_text
        combine_responses = chunker.combine_responses
        estimate_tokens = chunker.estimate_tokens

# Carrega chave do .env
load_dotenv()

def _check_research_env():
    if not os.getenv("API_OPENAI_KEY_RESEARCH"):
        raise RuntimeError("API_OPENAI_KEY_RESEARCH não configurada")

# Inicializa cliente OpenAI (será criado quando necessário)
client = None

def _get_client():
    """Retorna o cliente OpenAI, criando se necessário. Se OPENAI_API_BASE estiver definida (ex.: OpenRouter), usa como base_url."""
    global client
    if client is None:
        _check_research_env()
        api_key = os.getenv("API_OPENAI_KEY_RESEARCH")
        base_url = os.getenv("OPENAI_API_BASE")  # ex.: https://openrouter.ai/api/v1
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
    return client

def _chamar_nova_api(modelo, prompt, temperatura=None, max_output_tokens=None):
    """
    Chama a API do OpenRouter usando responses.create.
    
    Args:
        modelo: Nome do modelo
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2)
        max_output_tokens: Máximo de tokens de saída (padrão: 4000 para evitar erro 402)
    """
    cliente = _get_client()
    
    # Configurar max_output_tokens (padrão: 4000 para evitar erro de créditos)
    # Pode ser configurado via variável de ambiente
    if max_output_tokens is None:
        max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "4000"))
    
    # Limitar a 8000 tokens máximo para evitar erros de créditos
    max_output_tokens = min(max_output_tokens, 8000)
    
    params = {
        "model": modelo,
        "input": prompt,
        "max_output_tokens": max_output_tokens
    }
    
    # Adicionar temperatura se fornecida
    if temperatura is not None:
        params["temperature"] = temperatura
    
    response = cliente.responses.create(**params)
    return response.output_text

def gerar_resposta(prompt, temperatura=1, max_output_tokens=None):
    """
    Gera resposta usando modelo configurado (padrão: gpt-5-mini para velocidade).
    
    Args:
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2, padrão: 1)
        max_output_tokens: Máximo de tokens de saída (padrão: 4000)
    """
    _check_research_env()
    try:
        cliente = _get_client()
        # Permite configurar modelo via variável de ambiente, senão usa gpt-5-mini (mais rápido)
        modelo = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        
        # Log do valor exato da variável modelo antes da chamada
        logging.warning(f"[GPT_ENGINE] Modelo configurado: '{modelo}' (tipo: {type(modelo).__name__})")
        
        try:
            # Nova chamada da API que retorna diretamente o texto
            # max_output_tokens padrão: 4000 para evitar erro 402 (créditos insuficientes)
            resposta = _chamar_nova_api(modelo, prompt, temperatura, max_output_tokens)
            return resposta
        except Exception as e:
            # Log completo do erro incluindo a classe
            logging.error(f"[GPT_ENGINE] Erro na chamada da API:")
            logging.error(f"[GPT_ENGINE] Classe do erro: {e.__class__.__name__}")
            logging.error(f"[GPT_ENGINE] Mensagem completa: {str(e)}")
            logging.error(f"[GPT_ENGINE] Modelo usado: '{modelo}'")
            raise Exception(f"Erro ao gerar resposta: {str(e)} (classe: {e.__class__.__name__})")
    except Exception as e:
        logging.error(f"[GPT_ENGINE] Erro geral em gerar_resposta: {str(e)} (classe: {e.__class__.__name__})")
        raise Exception(f"Erro ao gerar resposta: {str(e)}")


def gerar_resposta_com_chunking(texto_longo, prompt_template, temperatura=0.4):
    """Processa texto longo em chunks."""
    chunks = chunk_text(texto_longo, chunk_size=3000, overlap=500)
    respostas = []
    
    for i, chunk in enumerate(chunks):
        prompt = prompt_template.format(chunk=chunk)
        resposta = gerar_resposta(prompt, temperatura)
        respostas.append(resposta)
    
    return combine_responses(respostas)


def resumir_chunks(chunks, max_tokens=1000):
    """Resume lista de chunks para reduzir tamanho."""
    resumos = []
    for i, chunk in enumerate(chunks):
        prompt = f"""
        Resuma este chunk de artigo científico de forma concisa, mantendo conceitos chave, métodos e conclusões.
        Foque em {max_tokens} tokens. Chunk {i+1}/{len(chunks)}:

        {chunk}
        """
        resumo = gerar_resposta(prompt, temperatura=0.2)
        resumos.append(resumo)
    
    prompt_final = f"Combine estes resumos de chunks em um texto coeso final:\n" + "\n\n".join(resumos)
    texto_final = gerar_resposta(prompt_final, temperatura=0.3)
    
    return texto_final