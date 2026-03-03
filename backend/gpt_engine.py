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
        if base_url and "openrouter.ai" in base_url:
            # Para OpenRouter, adicionar headers customizados
            # Nota: O cliente OpenAI pode não passar esses headers automaticamente
            # Vamos tentar configurar via default_headers
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
                logging.info(f"[GPT_ENGINE] Cliente OpenRouter configurado com headers: {list(default_headers.keys())}")
            except Exception as e:
                logging.warning(f"[GPT_ENGINE] Erro ao configurar headers, tentando sem headers: {e}")
                client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
    return client

def _chamar_nova_api(modelo, prompt, temperatura=None, max_output_tokens=None):
    """
    Chama a API do OpenRouter (ou OpenAI).
    OpenRouter usa chat/completions com messages; outros usos podem usar responses.create.
    
    Args:
        modelo: Nome do modelo
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2)
        max_output_tokens: Máximo de tokens de saída (padrão: 1000)
    """
    cliente = _get_client()
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
        
        # Re-raise com mensagem mais informativa
        raise Exception(f"Erro ao chamar API OpenRouter com modelo '{modelo}': {error_message}")

def _obter_modelos_fallback():
    """
    Retorna lista de modelos para tentar em ordem (fallback automático).
    Modelo principal: NVIDIA Nemotron Nano 12B 2 VL :free (gratuito no OpenRouter).
    Pode ser configurado via OPENAI_MODEL (modelo principal) e OPENAI_MODEL_FALLBACK (modelos alternativos separados por vírgula).
    """
    # Modelo principal padrão: NVIDIA Nemotron Nano 12B 2 VL - variante gratuita no OpenRouter
    modelo_principal = os.getenv("OPENAI_MODEL", "nvidia/nemotron-nano-12b-v2-vl:free")
    
    # Modelos de fallback (separados por vírgula)
    fallback_str = os.getenv("OPENAI_MODEL_FALLBACK", "openai/gpt-4o-mini,openai/gpt-3.5-turbo,anthropic/claude-3-haiku")
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
    Se receber erro 402 (créditos insuficientes), reduz automaticamente max_output_tokens.
    
    Args:
        prompt: Texto do prompt
        temperatura: Temperatura para geração (0-2, padrão: 1)
        max_output_tokens: Máximo de tokens de saída (padrão: 1000)
    """
    _check_research_env()
    
    modelos = _obter_modelos_fallback()
    cliente = _get_client()
    
    # Log do modelo principal configurado (para confirmar uso do Nemotron)
    logging.info(f"[GPT_ENGINE] Modelo principal: '{modelos[0]}' | Fallbacks: {modelos[1:]}")
    
    # Configurar max_output_tokens inicial se não fornecido
    if max_output_tokens is None:
        max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "1000"))
    
    ultimo_erro = None
    max_tokens_atual = max_output_tokens
    
    # Tentar cada modelo em ordem até um funcionar (Nemotron primeiro)
    for i, modelo in enumerate(modelos):
        try:
            logging.warning(f"[GPT_ENGINE] Tentando modelo {i+1}/{len(modelos)}: '{modelo}' (max_tokens={max_tokens_atual})")
            
            # Nova chamada da API que retorna diretamente o texto
            resposta = _chamar_nova_api(modelo, prompt, temperatura, max_tokens_atual)
            
            if i > 0:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo '{modelo}' funcionou (fallback)")
            else:
                logging.warning(f"[GPT_ENGINE] ✅ Modelo principal '{modelo}' funcionou")
            
            return resposta
            
        except Exception as e:
            ultimo_erro = e
            import traceback
            error_traceback = traceback.format_exc()
            
            # Verificar se é erro 402 (créditos insuficientes)
            is_402_error = False
            error_str = str(e).lower()
            if "402" in error_str or "credits" in error_str or "can only afford" in error_str:
                is_402_error = True
                # Reduzir max_output_tokens pela metade e tentar novamente com o mesmo modelo
                if max_tokens_atual > 50:  # Não reduzir abaixo de 50
                    max_tokens_atual = max(50, max_tokens_atual // 2)
                    logging.warning(f"[GPT_ENGINE] ⚠️ Erro 402 detectado! Reduzindo max_output_tokens para {max_tokens_atual}")
                    # Tentar novamente com o mesmo modelo e tokens reduzidos
                    try:
                        resposta = _chamar_nova_api(modelo, prompt, temperatura, max_tokens_atual)
                        logging.warning(f"[GPT_ENGINE] ✅ Sucesso após reduzir tokens para {max_tokens_atual}")
                        return resposta
                    except Exception as retry_error:
                        logging.error(f"[GPT_ENGINE] ❌ Falhou mesmo após reduzir tokens: {retry_error}")
                        ultimo_erro = retry_error
            
            if not is_402_error:
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