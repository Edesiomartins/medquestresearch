# Cache de respostas da LLM para evitar chamadas repetidas (mesmo prompt + tipo + temperatura).
# Em memória, com TTL opcional. Para produção com múltiplos workers, considere Redis.

import hashlib
import logging
import threading
import time
import os
from typing import Optional

# (key_str -> {"resposta": str, "timestamp": float, "expiry": float})
_cache: dict = {}
_lock = threading.Lock()
_DEFAULT_TTL_SEC = 3600  # 1 hora
_MAX_AGE_SEC = int(os.getenv("LLM_CACHE_MAX_AGE_SEC", str(7 * 24 * 60 * 60)))  # 7 dias


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
        now = time.time()
        timestamp = float(entry.get("timestamp", 0))
        expiry = float(entry.get("expiry", 0))
        resposta = entry.get("resposta")

        # Ignorar entradas muito antigas (segurança de memória e validade)
        if now - timestamp > _MAX_AGE_SEC:
            del _cache[key]
            return None
        if ttl > 0 and expiry < now:
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
    now = time.time()
    expiry = now + ttl if ttl > 0 else float("inf")
    with _lock:
        _cache[key] = {
            "resposta": resposta,
            "timestamp": now,
            "expiry": expiry,
        }


def clear_cache() -> None:
    """Limpa todo o cache (útil para testes ou memória)."""
    with _lock:
        _cache.clear()
        logging.info("[CACHE_LLM] cache limpo")


def limpar_cache_antigo(max_age_sec: Optional[int] = None) -> int:
    """
    Remove entradas antigas do cache e retorna quantidade removida.
    """
    limite = max_age_sec if max_age_sec is not None else _MAX_AGE_SEC
    now = time.time()
    removidos = 0
    with _lock:
        chaves = list(_cache.keys())
        for k in chaves:
            item = _cache.get(k) or {}
            ts = float(item.get("timestamp", 0))
            exp = float(item.get("expiry", 0))
            if (now - ts) > limite or exp < now:
                _cache.pop(k, None)
                removidos += 1
    if removidos:
        logging.info(f"[CACHE_LLM] limpeza concluída: {removidos} entradas removidas")
    return removidos
