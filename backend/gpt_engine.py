from __future__ import annotations

import os
import time
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

# Exceções do OpenAI (SDK v1+); fallback se não existirem
try:
    from openai import (
        AuthenticationError,
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
        BadRequestError,
    )
except ImportError:
    AuthenticationError = type("AuthenticationError", (Exception,), {})
    RateLimitError = type("RateLimitError", (Exception,), {})
    APIConnectionError = type("APIConnectionError", (Exception,), {})
    APITimeoutError = type("APITimeoutError", (Exception,), {})
    BadRequestError = type("BadRequestError", (Exception,), {})

# -----------------------------
# Imports locais (chunker, model_router, cache)
# -----------------------------
try:
    from .chunker import chunk_text, combine_responses, estimate_tokens
    from .model_router import modelos_para_tipo, MODELOS_FALLBACK
    from .cache_llm import get_cached, set_cached
except ImportError:
    try:
        from chunker import chunk_text, combine_responses, estimate_tokens
        from model_router import modelos_para_tipo, MODELOS_FALLBACK
        from cache_llm import get_cached, set_cached
    except ImportError:
        import backend.chunker as chunker
        import backend.model_router as model_router
        import backend.cache_llm as cache_llm
        chunk_text = chunker.chunk_text
        combine_responses = chunker.combine_responses
        estimate_tokens = chunker.estimate_tokens
        modelos_para_tipo = model_router.modelos_para_tipo
        MODELOS_FALLBACK = model_router.MODELOS_FALLBACK
        get_cached = cache_llm.get_cached
        set_cached = cache_llm.set_cached

# Carrega .env (desenvolvimento/local)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    parent_env = os.path.join(os.path.dirname(BASE_DIR), ".env")
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
    else:
        load_dotenv()

# -----------------------------
# Logging
# -----------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# -----------------------------
# Helpers de ENV
# -----------------------------
def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip()
    return val if val else default


def _normalize_secret(val: str) -> str:
    """Remove aspas envoltas comuns ao colar no Railway/.env e espaços."""
    s = (val or "").strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        s = s[1:-1].strip()
    return s


def _get_api_key(use_backup: bool = False) -> str:
    """
    Chave OpenRouter (sk-or-v1-...). Ordem intencional:
    1) OPENROUTER_API_KEY — nome recomendado
    2) API_OPENAI_KEY_RESEARCH — legado (muitos deploys Railway só têm esta)
    3) OPENROUTER_API_KEY_MAIN — evite duplicar: se estiver errada, apague ou corrija

    Antes OPENROUTER_API_KEY_MAIN vinha antes de API_OPENAI_KEY_RESEARCH e podia
    'sombrear' a chave legada com um valor vazio/placeholder no Railway.
    """
    if use_backup:
        return _normalize_secret(_env("OPENROUTER_API_KEY_BACKUP") or "")
    for name in (
        "OPENROUTER_API_KEY",
        "API_OPENAI_KEY_RESEARCH",
        "OPENROUTER_API_KEY_MAIN",
    ):
        raw = _env(name)
        if raw:
            return _normalize_secret(raw)
    return ""


def _check_research_env() -> None:
    if not _get_api_key(use_backup=False):
        raise RuntimeError(
            "Defina OPENROUTER_API_KEY ou API_OPENAI_KEY_RESEARCH (mesma chave sk-or-v1-... do OpenRouter). "
            "Se usar várias variáveis, remova valores vazios/placeholder — só uma chave válida é necessária."
        )


def _parse_models() -> List[str]:
    """Lista de modelos a partir de ENV. Se vazio, usa model_router em gerar_resposta."""
    main = _env("OPENROUTER_MODEL") or _env("OPENAI_MODEL")
    fb_raw = (_env("OPENROUTER_MODEL_FALLBACK", "") or _env("OPENAI_MODEL_FALLBACK", "") or "")
    fallbacks = [m.strip() for m in fb_raw.split(",") if m.strip()]
    models: List[str] = []
    if main:
        models.append(main)
    models.extend([m for m in fallbacks if m and m not in models])
    if not models:
        models = list(MODELOS_FALLBACK)
    return _prioritize_models(models)


def _prioritize_models(models: List[str]) -> List[str]:
    """
    Garante motores principais estáveis no topo da lista.
    Pode ser sobrescrito por ENV.
    """
    primary = (
        _env("OPENROUTER_MODEL_PRIMARY")
        or _env("OPENAI_MODEL_PRIMARY")
        or "nvidia/nemotron-3-super-120b-a12b:free"
    )
    secondary = (
        _env("OPENROUTER_MODEL_SECONDARY")
        or _env("OPENAI_MODEL_SECONDARY")
        or "openrouter/elephant-alpha"
    )
    ordered: List[str] = []
    for m in [primary, secondary] + list(models):
        if m and m not in ordered:
            ordered.append(m)
    return ordered


# -----------------------------
# Cache em memória (opcional)
# -----------------------------
_CACHE_ENABLED = (_env("LLM_CACHE_ENABLED", "true") or "true").lower() in ("1", "true", "yes", "on")
_CACHE_MAX_ITEMS = int(_env("LLM_CACHE_MAX_ITEMS", "200") or 200)
_cache: Dict[str, str] = {}
_cache_order: List[str] = []


def _cache_key(model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(str(temperature).encode("utf-8"))
    h.update(b"|")
    h.update(str(max_tokens).encode("utf-8"))
    h.update(b"|")
    h.update(prompt.encode("utf-8", errors="ignore")[:16000])
    return h.hexdigest()


def _cache_get(key: str) -> Optional[str]:
    if not _CACHE_ENABLED:
        return None
    return _cache.get(key)


def _cache_set(key: str, value: str) -> None:
    if not _CACHE_ENABLED:
        return
    if key in _cache:
        _cache[key] = value
        return
    _cache[key] = value
    _cache_order.append(key)
    while len(_cache_order) > _CACHE_MAX_ITEMS:
        old = _cache_order.pop(0)
        _cache.pop(old, None)


# -----------------------------
# Cliente OpenRouter
# -----------------------------
OPENAI_API_BASE = (
    _env("OPENROUTER_API_BASE")
    or _env("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
    or "https://openrouter.ai/api/v1"
)
HTTP_REFERER = _env("OPENROUTER_HTTP_REFERER") or _env("OPENROUTER_REFERRER", "https://medquestresearch.up.railway.app") or ""
APP_TITLE = _env("OPENROUTER_APP_TITLE", "MedQuestResearch") or "MedQuestResearch"

_client: Optional[OpenAI] = None
_client_use_backup = False
_MODEL_COOLDOWN_UNTIL: Dict[str, float] = {}
_MODEL_COOLDOWN_SECONDS = int(_env("OPENROUTER_MODEL_COOLDOWN_SECONDS", "900") or 900)


def _get_client(use_backup: bool = False) -> OpenAI:
    global _client, _client_use_backup
    if _client is not None and _client_use_backup == use_backup:
        return _client
    key = _get_api_key(use_backup=use_backup)
    if use_backup and not key:
        raise RuntimeError("OPENROUTER_API_KEY_BACKUP não configurada")
    if not use_backup:
        _check_research_env()
    _client = None
    _client_use_backup = use_backup
    base_url = OPENAI_API_BASE
    headers: Dict[str, str] = {}
    if base_url and "openrouter.ai" in base_url:
        headers = {"HTTP-Referer": HTTP_REFERER, "X-Title": APP_TITLE}
    try:
        _client = OpenAI(api_key=key, base_url=base_url, default_headers=headers)
    except Exception:
        _client = OpenAI(api_key=key, base_url=base_url)
    return _client


# -----------------------------
# Classificação de erros
# -----------------------------
def _is_rate_limit(err: Exception) -> bool:
    return isinstance(err, RateLimitError) or "429" in str(err)


def _is_auth(err: Exception) -> bool:
    return isinstance(err, AuthenticationError) or "401" in str(err) or "User not found" in str(err)


def _is_bad_request(err: Exception) -> bool:
    return isinstance(err, BadRequestError) or "400" in str(err)


def _is_transient(err: Exception) -> bool:
    # Caso especial: limite diário de modelos FREE da OpenRouter não deve gerar backoff infinito
    msg = str(err)
    if "free-models-per-day" in msg:
        return False
    return (
        isinstance(err, (RateLimitError, APIConnectionError, APITimeoutError))
        or "timeout" in msg.lower()
        or "rate" in msg.lower()
    )


def _is_provider_offline_error(err: Exception) -> bool:
    """
    Detecta indisponibilidade de provedor/modelo (ex.: modelo removido no OpenRouter).
    """
    msg = str(err).lower()
    return (
        "err_ngrok_3200" in msg
        or "openinference.ngrok.io is offline" in msg
        or ("provider returned error" in msg and "404" in msg and "openinference" in msg)
        or "no endpoints found" in msg
    )


# -----------------------------
# Chamada ao modelo (uma requisição)
# -----------------------------
def _call_chat_completion(
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout_s: int = 60,
    use_backup_key: bool = False,
) -> str:
    client = _get_client(use_backup=use_backup_key)
    params: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = client.chat.completions.create(**params, timeout=timeout_s)
    except TypeError:
        resp = client.chat.completions.create(**params)
    try:
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return str(resp).strip()


# -----------------------------
# API pública: gerar_resposta
# -----------------------------
def gerar_resposta(
    prompt: str,
    temperatura: float = 0.3,
    max_output_tokens: Optional[int] = None,
    tipo: str = "geral",
    timeout_s: int = 60,
    use_cache: bool = True,
) -> str:
    """
    Gera resposta via OpenRouter com fallback de modelos e retry.

    - Modelos: ENV (OPENROUTER_MODEL + OPENROUTER_MODEL_FALLBACK; legado OPENAI_*) ou model_router por tipo.
    - Cache opcional em memória (por model+prompt+temp+max_tokens).
    - Retry para 429/timeout; troca de modelo se persistir; 401 tenta chave backup.
    """
    _check_research_env()
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt vazio")

    max_tokens = max_output_tokens or int(_env("OPENROUTER_MAX_OUTPUT_TOKENS", "2500") or 2500)
    max_tokens = min(max_tokens, 4000)

    # Lista de modelos: ENV ou model_router por tipo
    models_from_env = _parse_models() if (_env("OPENROUTER_MODEL") or _env("OPENAI_MODEL")) else None
    if models_from_env and len(models_from_env) > 0:
        models = _prioritize_models(models_from_env)
    else:
        primarios = modelos_para_tipo(tipo)
        models = _prioritize_models(list(primarios) + [m for m in MODELOS_FALLBACK if m not in primarios])

    # Cache global (prompt+tipo+temp) para evitar rodar a lista inteira
    if use_cache and len(prompt) <= 8000:
        cached = get_cached(prompt, tipo, temperatura)
        if cached is not None:
            logger.info(f"[GPT_ENGINE] ({tipo}) Cache HIT (global)")
            return cached

    max_retries_per_model = int(_env("OPENROUTER_MAX_RETRIES", "3") or 3)
    base_backoff_s = float(_env("OPENROUTER_BACKOFF_SECONDS", "2.5") or 2.5)
    last_error: Optional[Exception] = None
    tried_backup = False

    for idx, model in enumerate(models, start=1):
        cooldown_until = _MODEL_COOLDOWN_UNTIL.get(model, 0.0)
        now = time.time()
        if cooldown_until > now:
            remaining = int(cooldown_until - now)
            logger.warning(
                f"[GPT_ENGINE] ({tipo}) Pulando modelo '{model}' por cooldown ({remaining}s restantes)."
            )
            continue

        logger.warning(f"[GPT_ENGINE] ({tipo}) Tentando modelo {idx}/{len(models)}: '{model}' (max_tokens={max_tokens})")

        cache_k = _cache_key(model, prompt, temperatura, max_tokens)
        cached = _cache_get(cache_k)
        if cached is not None:
            logger.info(f"[GPT_ENGINE] ({tipo}) Cache HIT para '{model}'")
            if use_cache and len(prompt) <= 8000:
                set_cached(prompt, tipo, temperatura, cached)
            return cached

        for attempt in range(1, max_retries_per_model + 1):
            try:
                text = _call_chat_completion(
                    model=model,
                    prompt=prompt,
                    temperature=temperatura,
                    max_tokens=max_tokens,
                    timeout_s=timeout_s,
                    use_backup_key=False,
                )
                if not text:
                    raise Exception("Resposta vazia do modelo")
                _cache_set(cache_k, text)
                if use_cache and len(prompt) <= 8000:
                    set_cached(prompt, tipo, temperatura, text)
                logger.info(f"[GPT_ENGINE] ({tipo}) ✅ Sucesso com '{model}' (tentativa {attempt}/{max_retries_per_model})")
                return text

            except Exception as e:
                last_error = e
                logger.error(
                    f"[GPT_ENGINE] ({tipo}) ❌ Erro | modelo='{model}' | tentativa {attempt}/{max_retries_per_model} | {e.__class__.__name__}: {e}"
                )

                # Caso especial: limite diário dos modelos gratuitos da OpenRouter.
                # Nessa situação, apenas pulamos para o próximo modelo (pode ser um modelo pago),
                # para permitir que o FREE seja o primário e o PAGO o fallback,
                # sem ficar aguardando com backoff.
                if "free-models-per-day" in str(e):
                    logger.warning(
                        "[GPT_ENGINE] (%s) Limite diario dos modelos gratuitos atingido para '%s'; tentando proximo modelo.",
                        tipo,
                        model,
                    )
                    break

                if _is_auth(e):
                    if _get_api_key(use_backup=True) and not tried_backup:
                        tried_backup = True
                        global _client
                        _client = None
                        logger.warning("[GPT_ENGINE] 401 na chave principal, tentando OPENROUTER_API_KEY_BACKUP...")
                        try:
                            text = _call_chat_completion(
                                model=model,
                                prompt=prompt,
                                temperature=temperatura,
                                max_tokens=max_tokens,
                                timeout_s=timeout_s,
                                use_backup_key=True,
                            )
                            if text:
                                _cache_set(cache_k, text)
                                if use_cache and len(prompt) <= 8000:
                                    set_cached(prompt, tipo, temperatura, text)
                                return text
                        except Exception as backup_err:
                            last_error = backup_err
                    raise Exception(
                        "Falha de autenticação (401) na OpenRouter. Verifique a chave no Railway e no painel OpenRouter."
                    )

                if _is_bad_request(e):
                    logger.warning(f"[GPT_ENGINE] ({tipo}) BadRequest (400), próximo modelo.")
                    break

                if _is_provider_offline_error(e):
                    _MODEL_COOLDOWN_UNTIL[model] = time.time() + _MODEL_COOLDOWN_SECONDS
                    logger.warning(
                        f"[GPT_ENGINE] ({tipo}) Provedor/modelo '{model}' indisponível (404/offline). "
                        f"Aplicando cooldown de {_MODEL_COOLDOWN_SECONDS}s e tentando próximo."
                    )
                    break

                if _is_transient(e):
                    sleep_s = base_backoff_s * attempt
                    logger.warning(f"[GPT_ENGINE] ({tipo}) ⚠️ Transiente (429/timeout). Aguardando {sleep_s:.1f}s...")
                    time.sleep(sleep_s)
                    continue

                logger.warning(f"[GPT_ENGINE] ({tipo}) Erro não-transiente, próximo modelo.")
                break

    raise Exception(
        f"Erro ao gerar resposta: todos os modelos falharam. "
        f"Modelos: {models}. Último erro: {last_error!s} ({type(last_error).__name__ if last_error else 'None'})"
    )


# -----------------------------
# Utilitário: gerar JSON
# -----------------------------
def gerar_resposta_json(
    prompt: str,
    temperatura: float = 0.2,
    max_tokens: int = 2500,
    tipo: str = "json",
    timeout_s: int = 60,
) -> Dict[str, Any]:
    """Chama gerar_resposta e tenta parsear JSON; extrai bloco {...} ou [...] se necessário."""
    text = gerar_resposta(
        prompt, temperatura=temperatura, max_output_tokens=max_tokens, tipo=tipo, timeout_s=timeout_s
    )
    try:
        return json.loads(text)
    except Exception:
        pass
    start_obj = text.find("{")
    end_obj = text.rfind("}")
    start_arr = text.find("[")
    end_arr = text.rfind("]")
    candidate = None
    if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
        candidate = text[start_obj : end_obj + 1]
    elif start_arr != -1 and end_arr != -1 and end_arr > start_arr:
        candidate = text[start_arr : end_arr + 1]
    if candidate:
        try:
            return json.loads(candidate)
        except Exception:
            pass
    raise ValueError("A resposta do modelo não é JSON válido (nem contém bloco JSON recuperável).")


# -----------------------------
# Chunking (compatibilidade)
# -----------------------------
def gerar_resposta_com_chunking(texto_longo: str, prompt_template: str, temperatura: float = 0.4) -> str:
    """Processa texto longo em chunks."""
    chunks = chunk_text(texto_longo, chunk_size=3000, overlap=500)
    respostas = []
    for chunk in chunks:
        prompt = prompt_template.format(chunk=chunk)
        respostas.append(gerar_resposta(prompt, temperatura=temperatura))
    return combine_responses(respostas)


def resumir_chunks(chunks: list, max_tokens: int = 1000) -> str:
    """Resume lista de chunks e combina em texto coeso."""
    resumos = []
    for i, chunk in enumerate(chunks):
        prompt = f"""Resuma este chunk de artigo científico de forma concisa, mantendo conceitos chave, métodos e conclusões.
Foque em {max_tokens} tokens. Chunk {i+1}/{len(chunks)}:

{chunk}
"""
        resumos.append(gerar_resposta(prompt, temperatura=0.2))
    prompt_final = "Combine estes resumos de chunks em um texto coeso final:\n\n" + "\n\n".join(resumos)
    return gerar_resposta(prompt_final, temperatura=0.3)
