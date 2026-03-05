import os
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Tentar importação relativa primeiro, depois absoluta
try:
    from .chunker import chunk_text, combine_responses, estimate_tokens
    from .model_router import escolher_modelo, MODELOS_FALLBACK
    from .cache_llm import get_cached, set_cached
except ImportError:
    try:
        from chunker import chunk_text, combine_responses, estimate_tokens
        from model_router import escolher_modelo, MODELOS_FALLBACK
        from cache_llm import get_cached, set_cached
    except ImportError:
        import backend.chunker as chunker
        import backend.model_router as model_router
        import backend.cache_llm as cache_llm
        chunk_text = chunker.chunk_text
        combine_responses = chunker.combine_responses
        estimate_tokens = chunker.estimate_tokens
        escolher_modelo = model_router.escolher_modelo
        MODELOS_FALLBACK = model_router.MODELOS_FALLBACK
        get_cached = cache_llm.get_cached
        set_cached = cache_llm.set_cached

# Carrega chave do .env (somente em desenvolvimento/local).
# Em produção (Railway), as variáveis já vêm do ambiente, então evitamos prints ruidosos.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logging.info(f"[GPT_ENGINE] Arquivo .env carregado de: {env_path}")
else:
    parent_env = os.path.join(os.path.dirname(BASE_DIR), '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
        logging.info(f"[GPT_ENGINE] Arquivo .env carregado de: {parent_env}")
    else:
        # Tenta carregar do diretório atual, mas sem logar warning se não existir.
        load_dotenv()

def _get_api_key(use_backup: bool = False) -> str:
    """Chave principal: API_OPENAI_KEY_RESEARCH ou OPENROUTER_API_KEY_MAIN. Backup: OPENROUTER_API_KEY_BACKUP."""
    if use_backup:
        return (os.getenv("OPENROUTER_API_KEY_BACKUP") or "").strip()
    return (os.getenv("API_OPENAI_KEY_RESEARCH") or os.getenv("OPENROUTER_API_KEY_MAIN") or "").strip()


def _check_research_env():
    if not _get_api_key(use_backup=False):
        raise RuntimeError("API_OPENAI_KEY_RESEARCH ou OPENROUTER_API_KEY_MAIN não configurada")

# Inicializa cliente OpenAI (será criado quando necessário); _client_use_backup indica se usamos chave backup
client = None
_client_use_backup = False

def _get_client(use_backup: bool = False):
    """Retorna o cliente OpenAI. use_backup=True usa OPENROUTER_API_KEY_BACKUP (após 401 na chave principal)."""
    global client, _client_use_backup
    if client is None or _client_use_backup != use_backup:
        key = _get_api_key(use_backup=use_backup)
        if use_backup and not key:
            raise RuntimeError("OPENROUTER_API_KEY_BACKUP não configurada")
        if not use_backup:
            _check_research_env()
        client = None
        _client_use_backup = use_backup
        api_key = key if use_backup else _get_api_key(use_backup=False)
        base_url = os.getenv("OPENAI_API_BASE")  # ex.: https://openrouter.ai/api/v1
        if base_url and "openrouter.ai" in base_url:
            default_headers = {
                "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "https://medquestresearch.up.railway.app"),
                "X-Title": os.getenv("OPENROUTER_TITLE", "MedQuestResearch"),
            }
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    default_headers=default_headers
                )
                logging.info(f"[GPT_ENGINE] Cliente OpenRouter configurado ({'backup' if use_backup else 'main'})")
            except Exception as e:
                logging.warning(f"[GPT_ENGINE] Erro ao configurar headers, tentando sem headers: {e}")
                client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
    return client

def _chamar_nova_api(modelo, prompt, temperatura=None, max_output_tokens=None, use_backup_key: bool = False):
    """
    Chama a API do OpenRouter (ou OpenAI).
    use_backup_key: usa OPENROUTER_API_KEY_BACKUP quando True (após 401 na chave principal).
    """
    cliente = _get_client(use_backup=use_backup_key)
    base_url = os.getenv("OPENAI_API_BASE", "")
    is_openrouter = base_url and "openrouter.ai" in base_url

    # Configurar max_output_tokens se não fornecido
    if max_output_tokens is None:
        max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "1000"))
    max_output_tokens = min(max_output_tokens, 2000)

    prompt_length = len(prompt) if prompt else 0
    if prompt_length > 10000:
        max_output_tokens = min(max_output_tokens, 500)
        logging.warning(f"[GPT_ENGINE] Prompt longo ({prompt_length} chars), reduzindo max_output_tokens para {max_output_tokens}")

    try:
        if is_openrouter:
            # OpenRouter: endpoint chat/completions com messages (formato esperado pelo Nemotron e demais modelos)
            params = {
                "model": modelo,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_output_tokens,
            }
            if temperatura is not None:
                params["temperature"] = temperatura
            response = cliente.chat.completions.create(**params)
            text = response.choices[0].message.content if response.choices else ""
            return text or ""
        else:
            # Compatibilidade: API Responses (ex.: OpenAI direto)
            params = {
                "model": modelo,
                "input": prompt,
                "max_output_tokens": max_output_tokens,
            }
            if temperatura is not None:
                params["temperature"] = temperatura
            response = cliente.responses.create(**params)
            if hasattr(response, 'output_text'):
                return response.output_text
            if hasattr(response, 'output') and isinstance(response.output, list) and len(response.output) > 0:
                first_output = response.output[0]
                if isinstance(first_output, dict) and 'content' in first_output:
                    return first_output['content']
                if isinstance(first_output, str):
                    return first_output
            if hasattr(response, 'output') and isinstance(response.output, str):
                return response.output
            return str(response)
    except Exception as e:
        # Log detalhado do erro
        import traceback
        error_traceback = traceback.format_exc()
        error_message = str(e)
        
        logging.error(f"[GPT_ENGINE] ❌ Erro ao chamar API:")
        logging.error(f"[GPT_ENGINE] Modelo: {modelo}")
        logging.error(f"[GPT_ENGINE] Erro: {error_message}")
        logging.error(f"[GPT_ENGINE] Tipo do erro: {type(e).__name__}")
        
        # Tentar extrair mais informações do erro da API
        if hasattr(e, 'status_code'):
            logging.error(f"[GPT_ENGINE] Status code: {e.status_code}")
        if hasattr(e, 'response'):
            try:
                if hasattr(e.response, 'text'):
                    response_text = e.response.text
                    logging.error(f"[GPT_ENGINE] Response text: {response_text}")
                    # Tentar parsear como JSON
                    try:
                        import json
                        error_json = json.loads(response_text)
                        logging.error(f"[GPT_ENGINE] Response JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        pass
                if hasattr(e.response, 'json'):
                    try:
                        error_json = e.response.json()
                        logging.error(f"[GPT_ENGINE] Response JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        pass
            except Exception as parse_error:
                logging.error(f"[GPT_ENGINE] Erro ao parsear resposta: {parse_error}")
        
        logging.error(f"[GPT_ENGINE] Traceback completo:\n{error_traceback}")
        
        # 401 = chave inválida/desativada: não tentar outros modelos com a mesma chave
        status_code = getattr(e, "status_code", None)
        if status_code == 401 or "401" in error_message:
            raise Exception("API key inválida ou desativada. Verifique OPENROUTER/API_OPENAI_KEY_RESEARCH no Railway.")
        raise Exception(f"Erro ao chamar API OpenRouter com modelo '{modelo}': {error_message}")

def gerar_resposta(prompt, temperatura=0.7, max_output_tokens=None, tipo="geral", use_cache=True):
    """
    Gera resposta usando o modelo escolhido pelo roteador para o tipo de tarefa, com fallback e cache opcional.

    Args:
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2, padrão: 0.7)
        max_output_tokens: Máximo de tokens de saída (padrão: 2500 ou env OPENROUTER_MAX_OUTPUT_TOKENS)
        tipo: Tipo de tarefa para o roteador (extracao, prisma, critica, explicacao, meta_analise, geral)
        use_cache: Se True, usa cache_llm para evitar chamadas repetidas (mesmo prompt+tipo+temperatura)
    """
    _check_research_env()

    if use_cache and prompt and len(prompt) <= 8000:
        cached = get_cached(prompt, tipo, temperatura)
        if cached is not None:
            return cached

    modelo_principal = escolher_modelo(tipo)
    # Lista: modelo do roteador primeiro, depois fallbacks (sem repetir o principal)
    modelos = [modelo_principal] + [m for m in MODELOS_FALLBACK if m != modelo_principal]

    if max_output_tokens is None:
        max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "2500"))

    logging.warning(f"[GPT_ENGINE] tipo={tipo} -> modelo '{modelo_principal}' | fallbacks: {modelos[1:] or 'nenhum'}")

    ultimo_erro = None
    max_tokens_atual = max_output_tokens
    tried_backup_key = False

    # Tentar modelo do roteador, depois fallbacks
    for i, modelo in enumerate(modelos):
        try:
            logging.warning(f"[GPT_ENGINE] Tentando modelo {i+1}/{len(modelos)}: '{modelo}' (max_tokens={max_tokens_atual})")
            resposta = _chamar_nova_api(modelo, prompt, temperatura, max_tokens_atual)
            if i > 0:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo '{modelo}' funcionou (fallback)")
            else:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo principal '{modelo}' funcionou")
            if use_cache and prompt and len(prompt) <= 8000:
                set_cached(prompt, tipo, temperatura, resposta)
            return resposta

        except Exception as e:
            ultimo_erro = e
            import traceback
            error_traceback = traceback.format_exc()
            error_str = str(e)
            status_code = getattr(e, "status_code", None)

            # 401 = chave inválida/desativada: uma tentativa com backup (se existir), senão falha na hora
            if status_code == 401 or "401" in error_str or "User not found" in error_str:
                if _get_api_key(use_backup=True) and not tried_backup_key:
                    tried_backup_key = True
                    try:
                        logging.warning("[GPT_ENGINE] 401 na chave principal, tentando OPENROUTER_API_KEY_BACKUP...")
                        global client
                        client = None
                        resposta = _chamar_nova_api(modelo, prompt, temperatura, max_tokens_atual, use_backup_key=True)
                        if use_cache and prompt and len(prompt) <= 8000:
                            set_cached(prompt, tipo, temperatura, resposta)
                        return resposta
                    except Exception:
                        pass
                raise Exception("API key inválida ou desativada. Verifique a chave no Railway e no painel OpenRouter.")

            # Verificar se é erro 402 (créditos insuficientes)
            is_402_error = False
            if "402" in error_str or "credits" in error_str or "can only afford" in error_str:
                is_402_error = True
                if max_tokens_atual > 50:
                    max_tokens_atual = max(50, max_tokens_atual // 2)
                    logging.warning(f"[GPT_ENGINE] ⚠️ Erro 402 detectado! Reduzindo max_output_tokens para {max_tokens_atual}")
                    try:
                        resposta = _chamar_nova_api(modelo, prompt, temperatura, max_tokens_atual)
                        logging.warning(f"[GPT_ENGINE] ✅ Sucesso após reduzir tokens para {max_tokens_atual}")
                        if use_cache and prompt and len(prompt) <= 8000:
                            set_cached(prompt, tipo, temperatura, resposta)
                        return resposta
                    except Exception as retry_error:
                        logging.error(f"[GPT_ENGINE] ❌ Falhou mesmo após reduzir tokens: {retry_error}")
                        ultimo_erro = retry_error

            if not is_402_error:
                logging.warning(f"[GPT_ENGINE] ⚠️ Modelo '{modelo}' falhou, tentando próximo...")
                logging.error(f"[GPT_ENGINE] Erro: {str(e)} (classe: {e.__class__.__name__})")

            # Pausa entre modelos para evitar rate-limit/desativação pela OpenRouter
            if i < len(modelos) - 1:
                time.sleep(1.5)
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