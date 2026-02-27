from fastapi import APIRouter, Request, HTTPException
import os

router = APIRouter(prefix="/genapi", tags=["asaas"])


@router.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    # Asaas envia o token no header "asaas-access-token" (docs Asaas)
    token_recebido = (
        request.headers.get("asaas-access-token")
        or request.headers.get("Asaas-Access-Token")
        or request.headers.get("access_token")
        or request.headers.get("accessToken")
        or request.headers.get("Access-Token")
    )
    token_esperado = os.getenv("ASAAS_WEBHOOK_TOKEN")

    print("HEADERS:", dict(request.headers))
    print("TOKEN RECEBIDO:", repr(token_recebido))
    print("TOKEN ESPERADO:", repr(token_esperado))

    if not token_esperado:
        raise HTTPException(
            status_code=503,
            detail="Servidor sem ASAAS_WEBHOOK_TOKEN configurado. Defina a variável de ambiente com o token do webhook no painel Asaas.",
        )
    if not token_recebido:
        raise HTTPException(
            status_code=403,
            detail="Header asaas-access-token ausente. No painel Asaas, edite o webhook e preencha o 'Token de autenticação' (ou gere um novo) e use o mesmo valor em ASAAS_WEBHOOK_TOKEN.",
        )
    if token_recebido != token_esperado:
        raise HTTPException(status_code=403, detail="Token inválido")

    data = await request.json()

    print("📩 Webhook recebido:", data)

    return {"status": "ok"}
