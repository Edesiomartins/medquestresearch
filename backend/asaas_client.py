"""
Cliente HTTP para API Asaas v3: criar cliente (customer) e cobrança (payment).
Usado pelo endpoint POST /genapi/checkout/creditos.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

ASAAS_BASE_URL = os.getenv("ASAAS_BASE_URL", "https://api.asaas.com/v3")
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
SANDBOX = os.getenv("ASAAS_SANDBOX", "").lower() in ("1", "true", "yes")
if SANDBOX:
    ASAAS_BASE_URL = os.getenv("ASAAS_BASE_URL", "https://sandbox.asaas.com/api/v3")

# Regra de preço (igual ao restante do sistema)
PRECO_CREDITO = 0.25
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20


def _headers() -> dict:
    if not ASAAS_API_KEY:
        raise ValueError("ASAAS_API_KEY não configurada")
    return {
        "access_token": ASAAS_API_KEY,
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    return ASAAS_BASE_URL.rstrip("/")


def calcular_valor_reais(quantidade: int) -> float:
    """Valor em R$ para a quantidade de créditos (valor = quantidade * PRECO_CREDITO)."""
    return round(quantidade * PRECO_CREDITO, 2)


def calcular_creditos_entregues(quantidade: int) -> int:
    """Créditos que o usuário receberá (com bônus se quantidade > 300)."""
    bonus = 0
    if quantidade > BONUS_THRESHOLD:
        bonus = int(quantidade * BONUS_PERCENT)
    return quantidade + bonus


def criar_cliente(nome: str, email: str, cpf_cnpj: Optional[str] = None, telefone: Optional[str] = None) -> dict:
    """
    Cria um cliente no Asaas. Retorna o JSON da resposta com 'id' (ex: cus_xxx).
    Campos obrigatórios na API: name, cpfCnpj, mobilePhone. Email recomendado.
    """
    payload = {
        "name": nome or "Cliente",
        "email": email or "",
        "cpfCnpj": (cpf_cnpj or "").replace(".", "").replace("-", "").replace("/", "") or "00000000000",
        "mobilePhone": (telefone or "").replace(" ", "").replace("-", "") or "11999999999",
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{_base_url()}/customers",
            headers=_headers(),
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
        logging.info(f"[ASAAS] Cliente criado: {data.get('id')}")
        return data


def criar_cobranca(
    customer_id: str,
    valor: float,
    descricao: str,
    external_reference: str,
    due_days: int = 3,
    billing_type: str = "BOLETO",
) -> dict:
    """
    Cria uma cobrança no Asaas. Retorna o JSON com invoiceUrl, id, etc.
    """
    due = (datetime.utcnow() + timedelta(days=due_days)).strftime("%Y-%m-%d")
    payload = {
        "customer": customer_id,
        "billingType": billing_type,
        "value": round(valor, 2),
        "dueDate": due,
        "description": descricao[:500] if descricao else "Créditos MedQuestResearch",
        "externalReference": external_reference,
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{_base_url()}/payments",
            headers=_headers(),
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
        logging.info(f"[ASAAS] Cobrança criada: {data.get('id')} -> {data.get('invoiceUrl')}")
        return data
