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
# Garantir que carrega do diretório correto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[GPT_ENGINE] ✅ Arquivo .env carregado de: {env_path}")
else:
    # Tentar carregar do diretório pai (se executado da raiz)
    parent_env = os.path.join(os.path.dirname(BASE_DIR), '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
        print(f"[GPT_ENGINE] ✅ Arquivo .env carregado de: {parent_env}")
    else:
        load_dotenv()  # Tentar carregar do diretório atual
        print(f"[GPT_ENGINE] ⚠️ Tentando carregar .env do diretório atual")

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
            # Para OpenRouter, adicionar headers customizados
            default_headers = {
                "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "https://medquestresearch.up.railway.app"),
                "X-Title": os.getenv("OPENROUTER_TITLE", "MedQuestResearch"),
            }
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers=default_headers
            )
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
    
    try:
        response = cliente.responses.create(**params)
        # Verificar se a resposta tem output_text
        if hasattr(response, 'output_text'):
            return response.output_text
        elif hasattr(response, 'output') and isinstance(response.output, list) and len(response.output) > 0:
            # Se for formato de array, pegar o primeiro conteúdo
            first_output = response.output[0]
            if isinstance(first_output, dict) and 'content' in first_output:
                return first_output['content']
            elif isinstance(first_output, str):
                return first_output
        elif hasattr(response, 'output') and isinstance(response.output, str):
            return response.output
        else:
            # Fallback: tentar converter para string
            logging.warning(f"[GPT_ENGINE] Formato de resposta inesperado: {type(response)}")
            return str(response)
    except Exception as e:
        # Log detalhado do erro
        logging.error(f"[GPT_ENGINE] Erro ao chamar API OpenRouter:")
        logging.error(f"[GPT_ENGINE] Modelo: {modelo}")
        logging.error(f"[GPT_ENGINE] Parâmetros: {params}")
        logging.error(f"[GPT_ENGINE] Erro: {e}")
        logging.error(f"[GPT_ENGINE] Tipo do erro: {type(e).__name__}")
        raise

def _obter_modelos_fallback():
    """
    Retorna lista de modelos para tentar em ordem (fallback automático).
    Pode ser configurado via OPENAI_MODEL (modelo principal) e OPENAI_MODEL_FALLBACK (modelos alternativos separados por vírgula).
    """
    modelo_principal = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    
    # Modelos de fallback (separados por vírgula)
    fallback_str = os.getenv("OPENAI_MODEL_FALLBACK", "openai/gpt-4o-mini,openai/gpt-3.5-turbo")
    modelos_fallback = [m.strip() for m in fallback_str.split(",") if m.strip()]
    
    # Lista completa: modelo principal primeiro, depois fallbacks
    modelos = [modelo_principal] + modelos_fallback
    
    # Remover duplicatas mantendo ordem
    modelos_unicos = []
    for modelo in modelos:
        if modelo not in modelos_unicos:
            modelos_unicos.append(modelo)
    
    return modelos_unicos

def gerar_resposta(prompt, temperatura=1, max_output_tokens=None):
    """
    Gera resposta usando modelo configurado com fallback automático.
    
    Se o modelo principal falhar, tenta automaticamente os modelos de fallback.
    
    Args:
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2, padrão: 1)
        max_output_tokens: Máximo de tokens de saída (padrão: 4000)
    """
    _check_research_env()
    
    modelos = _obter_modelos_fallback()
    cliente = _get_client()
    
    ultimo_erro = None
    
    # Tentar cada modelo em ordem até um funcionar
    for i, modelo in enumerate(modelos):
        try:
            logging.warning(f"[GPT_ENGINE] Tentando modelo {i+1}/{len(modelos)}: '{modelo}'")
            
            # Nova chamada da API que retorna diretamente o texto
            resposta = _chamar_nova_api(modelo, prompt, temperatura, max_output_tokens)
            
            if i > 0:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo '{modelo}' funcionou (fallback)")
            else:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo principal '{modelo}' funcionou")
            
            return resposta
            
        except Exception as e:
            ultimo_erro = e
            import traceback
            error_traceback = traceback.format_exc()
            
            logging.warning(f"[GPT_ENGINE] ⚠️ Modelo '{modelo}' falhou, tentando próximo...")
            logging.error(f"[GPT_ENGINE] Erro: {str(e)} (classe: {e.__class__.__name__})")
            
            # Se não for o último modelo, continuar tentando
            if i < len(modelos) - 1:
                continue
            else:
                # Último modelo falhou, log completo e lançar erro
                logging.error(f"[GPT_ENGINE] ❌ Todos os modelos falharam!")
                logging.error(f"[GPT_ENGINE] Modelos tentados: {modelos}")
                logging.error(f"[GPT_ENGINE] Traceback completo:\n{error_traceback}")
                
                # Se for erro de API, incluir mais detalhes
                if hasattr(e, 'response'):
                    try:
                        error_body = e.response.text if hasattr(e.response, 'text') else str(e.response)
                        logging.error(f"[GPT_ENGINE] Resposta do erro: {error_body}")
                    except:
                        pass
                
                raise Exception(f"Erro ao gerar resposta: Todos os modelos falharam. Último erro: {str(ultimo_erro)} (classe: {ultimo_erro.__class__.__name__})")
    
    # Se chegou aqui, algo deu errado
    raise Exception(f"Erro ao gerar resposta: Nenhum modelo disponível")


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