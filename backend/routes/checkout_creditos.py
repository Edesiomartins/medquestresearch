"""
POST /genapi/checkout/creditos: gera cobrança PIX no Asaas para compra de créditos.
Requer usuário autenticado (Bearer token) e asaas_customer_id preenchido.
"""

from datetime import datetime, timedelta
import os

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

try:
    from backend.database import get_connection, db_select_one
except ImportError:
    try:
        from database import get_connection, db_select_one
    except ImportError:
        from ..database import get_connection, db_select_one

router = APIRouter(prefix="/genapi", tags=["checkout"])

PRECO_CREDITO = 0.25
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20


class CheckoutCreditosRequest(BaseModel):
    quantidade: int


async def get_current_user(authorization: str = Header(None)):
    """Autentica pelo header Authorization: Bearer <token> e retorna o usuário."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")
    user = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(user)


@router.post("/checkout/creditos")
async def checkout_creditos(
    body: CheckoutCreditosRequest,
    current_user: dict = Depends(get_current_user),
):
    if body.quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade inválida")

    quantidade = body.quantidade
    valor = round(quantidade * PRECO_CREDITO, 2)

    bonus = 0
    if quantidade > BONUS_THRESHOLD:
        bonus = int(quantidade * BONUS_PERCENT)

    creditos_finais = quantidade + bonus

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT asaas_customer_id FROM usuarios WHERE id = %s",
                (current_user["id"],),
            )
            result = cursor.fetchone()
    finally:
        conn.close()

    asaas_customer_id = result.get("asaas_customer_id") if result else None
    if not asaas_customer_id:
        raise HTTPException(
            status_code=400,
            detail="Usuário sem asaas_customer_id. Registre-se no gateway de pagamento antes de comprar créditos.",
        )

    base_url = (os.getenv("ASAAS_BASE_URL") or "https://api.asaas.com/v3").rstrip("/")
    api_key = os.getenv("ASAAS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Checkout não configurado (ASAAS_API_KEY).")

    due_date = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d")
    payload = {
        "customer": asaas_customer_id,
        "billingType": "PIX",
        "value": valor,
        "dueDate": due_date,
        "description": f"Compra de {quantidade} créditos (+{bonus} bônus)",
        "externalReference": f"uid_{current_user['id']}_credits_{creditos_finais}",
    }

    headers = {
        "access_token": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/payments",
            json=payload,
            headers=headers,
        )

    if response.status_code >= 400:
        try:
            err = response.json()
        except Exception:
            err = {"detail": response.text}
        raise HTTPException(status_code=502, detail=err)

    data = response.json()

    return {
        "invoiceUrl": data.get("invoiceUrl"),
        "valor": valor,
        "creditos_finais": creditos_finais,
    }
