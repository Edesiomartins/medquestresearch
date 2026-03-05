# Cache de respostas da LLM para evitar chamadas repetidas (mesmo prompt + tipo + temperatura).
# Em memória, com TTL opcional. Para produção com múltiplos workers, considere Redis.

import hashlib
import logging
import threading
import time
from typing import Optional

# (key_str -> (resposta, expiry_ts))
_cache: dict = {}
_lock = threading.Lock()
_DEFAULT_TTL_SEC = 3600  # 1 hora


def _cache_key(prompt: str, tipo: str, temperatura: float) -> str:
    raw = f"{prompt[:5000]}|{tipo}|{temperatura}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cached(prompt: str, tipo: str, temperatura: float, ttl_sec: Optional[int] = None) -> Optional[str]:
    """
    Retorna resposta em cache se existir e não estiver expirada.
    ttl_sec: se None, usa padrão (1h). 0 = não expira.
    """
    key = _cache_key(prompt, tipo, temperatura)
    ttl = ttl_sec if ttl_sec is not None else _DEFAULT_TTL_SEC
    with _lock:
        entry = _cache.get(key)
        if not entry:
            return None
        resposta, expiry = entry
        if ttl > 0 and expiry < time.time():
            del _cache[key]
            return None
        logging.info("[CACHE_LLM] hit")
        return resposta


def set_cached(
    prompt: str,
    tipo: str,
    temperatura: float,
    resposta: str,
    ttl_sec: Optional[int] = None,
) -> None:
    """Armazena resposta no cache com TTL opcional."""
    key = _cache_key(prompt, tipo, temperatura)
    ttl = ttl_sec if ttl_sec is not None else _DEFAULT_TTL_SEC
    expiry = time.time() + ttl if ttl > 0 else float("inf")
    with _lock:
        _cache[key] = (resposta, expiry)


def clear_cache() -> None:
    """Limpa todo o cache (útil para testes ou memória)."""
    with _lock:
        _cache.clear()
        logging.info("[CACHE_LLM] cache limpo")
