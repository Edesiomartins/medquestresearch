from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

try:
    from backend.database import db_select_one
except Exception:
    from database import db_select_one  # type: ignore

try:
    from backend.gpt_engine import gerar_resposta_openrouter_free_chat
except Exception:
    from gpt_engine import gerar_resposta_openrouter_free_chat  # type: ignore


router = APIRouter(prefix="/api/help", tags=["help-chat"])


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
    model_tier: str = "openrouter_free"


@router.post("/chat", response_model=HelpChatResponse)
def help_chat(payload: HelpChatRequest, user=Depends(require_api_key)):
    _ = user
    try:
        answer = gerar_resposta_openrouter_free_chat(
            user_message=payload.message,
            history=[item.dict() for item in (payload.history or [])],
            max_output_tokens=900,
        )
        return HelpChatResponse(answer=answer)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Chat de ajuda indisponível: {error}")

