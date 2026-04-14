from __future__ import annotations

import os
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

try:
    from backend.database import db_execute, db_select, db_select_one
except Exception:
    from database import db_execute, db_select, db_select_one  # type: ignore

try:
    from backend.gpt_engine import gerar_resposta_openrouter_free_chat
except Exception:
    from gpt_engine import gerar_resposta_openrouter_free_chat  # type: ignore


router = APIRouter(prefix="/api/help", tags=["help-chat"])
_TABLE_READY = False
_MANUAL_CACHE: Optional[str] = None

ACRONYM_GLOSSARY = {
    "PRISMA": "Preferred Reporting Items for Systematic Reviews and Meta-Analyses; guia de transparência para revisões sistemáticas.",
    "PICO": "Paciente/População, Intervenção, Comparador e Outcome (desfecho); estrutura da pergunta clínica.",
    "SMD": "Standardized Mean Difference (diferença média padronizada), comum em desfechos contínuos com escalas distintas.",
    "RR": "Risk Ratio (razão de risco); compara risco de evento entre intervenção e comparador.",
    "OR": "Odds Ratio (razão de chances); compara as chances de evento entre grupos.",
    "CI95": "Intervalo de confiança de 95%, faixa plausível do efeito estimado.",
    "I²": "Percentual da heterogeneidade entre estudos não explicada pelo acaso.",
    "tau²": "Variância entre estudos em modelos de efeitos aleatórios.",
    "REML": "Restricted Maximum Likelihood; método para estimar heterogeneidade (tau²).",
    "DL": "DerSimonian-Laird; método clássico de efeitos aleatórios.",
    "PM": "Paule-Mandel; método alternativo para estimativa de heterogeneidade.",
    "Egger": "Teste estatístico para avaliar assimetria de funnel plot (possível viés de publicação).",
    "Begg": "Teste baseado em correlação para investigar viés de publicação.",
}


def _ensure_help_chat_table() -> None:
    global _TABLE_READY
    if _TABLE_READY:
        return
    db_execute(
        """
        CREATE TABLE IF NOT EXISTS public.help_chat_messages (
            id BIGSERIAL PRIMARY KEY,
            usuario_id BIGINT NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )
    db_execute(
        """
        CREATE INDEX IF NOT EXISTS idx_help_chat_messages_usuario_created
        ON public.help_chat_messages (usuario_id, created_at DESC);
        """
    )
    _TABLE_READY = True


def _load_manual_context() -> str:
    global _MANUAL_CACHE
    if _MANUAL_CACHE is not None:
        return _MANUAL_CACHE
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(backend_dir)
    manual_path = os.path.join(root_dir, "docs", "MANUAL_USUARIO_WEBAPP.md")
    try:
        with open(manual_path, "r", encoding="utf-8") as stream:
            _MANUAL_CACHE = stream.read()
    except Exception:
        _MANUAL_CACHE = ""
    return _MANUAL_CACHE


def require_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    token = authorization.replace("Bearer ", "").strip()
    user = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(user)


class ChatMessage(BaseModel):
    role: str = Field(..., description="user|assistant")
    content: str


class HelpChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)


class HelpChatResponse(BaseModel):
    answer: str
    model_tier: str = "openrouter_elephant_alpha"


class HelpHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: Optional[str] = None


class HelpHistoryResponse(BaseModel):
    messages: List[HelpHistoryItem]


def _get_recent_history(usuario_id: int, limit: int = 12) -> List[dict]:
    _ensure_help_chat_table()
    rows = db_select(
        """
        SELECT id, role, content, created_at
        FROM public.help_chat_messages
        WHERE usuario_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (usuario_id, limit),
    )
    rows = list(reversed(rows or []))
    history: List[dict] = []
    for row in rows:
        history.append(
            {
                "id": row.get("id"),
                "role": row.get("role"),
                "content": row.get("content"),
                "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
            }
        )
    return history


@router.post("/chat", response_model=HelpChatResponse)
def help_chat(payload: HelpChatRequest, user=Depends(require_api_key)):
    usuario_id = int(user["id"])
    try:
        _ensure_help_chat_table()
        db_execute(
            """
            INSERT INTO public.help_chat_messages (usuario_id, role, content)
            VALUES (%s, 'user', %s)
            """,
            (usuario_id, payload.message.strip()),
        )
        history = _get_recent_history(usuario_id, limit=12)
        answer = gerar_resposta_openrouter_free_chat(
            user_message=payload.message,
            history=[{"role": item["role"], "content": item["content"]} for item in history],
            knowledge_context=_load_manual_context(),
            acronym_glossary=ACRONYM_GLOSSARY,
            max_output_tokens=900,
        )
        db_execute(
            """
            INSERT INTO public.help_chat_messages (usuario_id, role, content)
            VALUES (%s, 'assistant', %s)
            """,
            (usuario_id, answer),
        )
        return HelpChatResponse(answer=answer)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Chat de ajuda indisponível: {error}")


@router.get("/history", response_model=HelpHistoryResponse)
def help_history(limit: int = 50, user=Depends(require_api_key)):
    usuario_id = int(user["id"])
    cap = max(1, min(limit, 200))
    messages = _get_recent_history(usuario_id, limit=cap)
    return HelpHistoryResponse(messages=[HelpHistoryItem(**row) for row in messages])


@router.delete("/history")
def clear_help_history(user=Depends(require_api_key)):
    usuario_id = int(user["id"])
    _ensure_help_chat_table()
    db_execute(
        "DELETE FROM public.help_chat_messages WHERE usuario_id = %s",
        (usuario_id,),
    )
    return {"status": "success", "message": "Histórico de chat removido."}

