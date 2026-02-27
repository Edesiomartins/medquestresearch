from fastapi import APIRouter, Request, HTTPException
import os

router = APIRouter(prefix="/genapi", tags=["asaas"])


@router.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    # 🔐 Validar token do webhook
    token_recebido = request.headers.get("access_token") or request.headers.get("accessToken")
    token_esperado = os.getenv("ASAAS_WEBHOOK_TOKEN")

    if not token_esperado or token_recebido != token_esperado:
        raise HTTPException(status_code=403, detail="Token inválido")

    data = await request.json()

    print("📩 Webhook recebido:", data)

    return {"status": "ok"}
