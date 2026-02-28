"""
POST /genapi/checkout/creditos: gera cobrança PIX no Asaas para compra de créditos.
Se o usuário não tiver asaas_customer_id, cria o cliente no Asaas (com cpfCnpj e mobilePhone obrigatórios).
"""

from datetime import datetime, timedelta
import logging
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

try:
    from backend.asaas_client import criar_cliente as asaas_criar_cliente
except ImportError:
    try:
        from asaas_client import criar_cliente as asaas_criar_cliente
    except ImportError:
        from ..asaas_client import criar_cliente as asaas_criar_cliente

def get_current_user(authorization: str = Header(None)):
    """Extrai token do header (Bearer ou puro) e busca usuário no banco."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")
    row = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not row:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(row)

router = APIRouter(prefix="/genapi", tags=["checkout"])

PRECO_CREDITO = 0.25
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20


class CheckoutCreditosRequest(BaseModel):
    quantidade: int


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
        asaas_customer_id = result.get("asaas_customer_id") if result else None
    finally:
        conn.close()

    # Se não tem cliente Asaas, criar (API exige name, cpfCnpj e mobilePhone válidos)
    if not asaas_customer_id:
        nome = (current_user.get("nome") or "").strip() or "Cliente"
        email = (current_user.get("email") or "").strip()
        cpf = (current_user.get("cpf") or "").strip()
        telefone = (current_user.get("telefone") or "").strip()
        if not cpf or not telefone:
            raise HTTPException(
                status_code=400,
                detail="Para comprar créditos, atualize seu cadastro com CPF e telefone em Meus dados.",
            )
        try:
            customer = asaas_criar_cliente(nome=nome, email=email, cpf_cnpj=cpf, telefone=telefone)
            asaas_customer_id = customer.get("id")
        except Exception as e:
            logging.exception("[CHECKOUT] Erro ao criar cliente Asaas: %s", e)
            raise HTTPException(
                status_code=400,
                detail="Dados de CPF ou telefone inválidos. Atualize em Meus dados com valores válidos.",
            )
        if not asaas_customer_id:
            raise HTTPException(status_code=502, detail="Resposta inválida do gateway ao criar cliente.")
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET asaas_customer_id = %s WHERE id = %s",
                    (asaas_customer_id, current_user["id"]),
                )
            conn.commit()
        finally:
            conn.close()

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
