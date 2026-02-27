"""
Webhook Asaas: processa PAYMENT_RECEIVED, credita usuário e registra pagamento.

Requer no banco:
- usuarios.asaas_customer_id (VARCHAR, nullable) – ID do cliente no Asaas (ex: cus_000143719698)
- Tabela pagamentos com: usuario_id, payment_asaas_id (único), referencia, valor, evento, creditos_adicionados, created_at
"""

from fastapi import APIRouter, Request, HTTPException
import os

# Regra de monetização (igual api.py)
PRECO_CREDITO = 0.25
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20

try:
    from ..database import get_connection
except ImportError:
    try:
        from database import get_connection
    except ImportError:
        from backend.database import get_connection  # type: ignore

router = APIRouter(prefix="/genapi", tags=["asaas"])


def _calcular_creditos_entregues(quantidade: int) -> int:
    bonus = 0
    if quantidade > BONUS_THRESHOLD:
        bonus = int(quantidade * BONUS_PERCENT)
    return quantidade + bonus


def _adicionar_creditos(usuario_id: int, qtd: int) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE usuarios SET creditos = creditos + %s WHERE id = %s",
                (qtd, usuario_id),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"[ASAAS WEBHOOK] Erro ao adicionar créditos: {e}")
        return False
    finally:
        conn.close()


@router.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    token_recebido = (
        request.headers.get("asaas-access-token")
        or request.headers.get("Asaas-Access-Token")
        or request.headers.get("access_token")
        or request.headers.get("accessToken")
        or request.headers.get("Access-Token")
    )
    token_esperado = os.getenv("ASAAS_WEBHOOK_TOKEN")

    if not token_esperado:
        raise HTTPException(
            status_code=503,
            detail="ASAAS_WEBHOOK_TOKEN não configurado.",
        )
    if not token_recebido or token_recebido != token_esperado:
        raise HTTPException(status_code=403, detail="Token inválido")

    data = await request.json()
    evento = data.get("event")
    payment = data.get("payment") or {}

    if evento not in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
        return {"status": "ignorado", "evento": evento}

    customer_id = payment.get("customer")
    value = payment.get("value")
    payment_id = payment.get("id")
    reference = payment.get("externalReference")

    if not payment_id:
        return {"status": "ok", "erro": "payload sem payment.id"}

    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Idempotência: já processamos este payment?
                cur.execute(
                    "SELECT id FROM pagamentos WHERE payment_asaas_id = %s",
                    (payment_id,),
                )
                if cur.fetchone():
                    conn.close()
                    return {"status": "ok", "ja_processado": True}

                usuario_id = None
                creditos = 0

                # Formato checkout_creditos: uid_15_credits_480
                if reference and "_" in str(reference):
                    partes = str(reference).split("_")
                    if len(partes) >= 4 and partes[0] == "uid" and partes[2] == "credits":
                        try:
                            usuario_id = int(partes[1])
                            creditos = int(partes[3])
                        except (ValueError, IndexError):
                            pass

                if usuario_id is not None and creditos > 0:
                    if not _adicionar_creditos(usuario_id, creditos):
                        conn.close()
                        raise HTTPException(status_code=500, detail="Falha ao adicionar créditos")
                    cur.execute(
                        """
                        INSERT INTO pagamentos (usuario_id, payment_asaas_id, referencia, valor, evento, creditos_adicionados)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (usuario_id, payment_id, reference, value, evento, creditos),
                    )
                    conn.commit()
                    return {"status": "ok", "creditos_adicionados": creditos}

                # Fluxo legado: buscar usuário pelo customer Asaas + pacote_N ou valor
                if not customer_id:
                    conn.close()
                    return {"status": "ok", "erro": "sem_referencia_valida"}

                cur.execute(
                    "SELECT id FROM usuarios WHERE asaas_customer_id = %s",
                    (customer_id,),
                )
                row = cur.fetchone()
                if not row:
                    conn.close()
                    print(f"[ASAAS WEBHOOK] Usuário não encontrado para customer={customer_id}")
                    return {"status": "ok", "erro": "usuario_nao_encontrado"}

                usuario_id = row["id"] if isinstance(row, dict) else row[0]

                # Calcular créditos: pacote_N ou valor/PRECO_CREDITO
                quantidade = 0
                if reference and str(reference).startswith("pacote_"):
                    try:
                        quantidade = int(str(reference).replace("pacote_", "").strip())
                    except ValueError:
                        pass
                if quantidade <= 0 and value is not None:
                    try:
                        quantidade = int(round(float(value) / PRECO_CREDITO))
                    except (ValueError, TypeError):
                        pass

                if quantidade <= 0:
                    conn.close()
                    return {"status": "ok", "erro": "nao_foi_possivel_calcular_creditos"}

                creditos = _calcular_creditos_entregues(quantidade)

                if not _adicionar_creditos(usuario_id, creditos):
                    conn.close()
                    raise HTTPException(status_code=500, detail="Falha ao adicionar créditos")

                # Registrar pagamento (tabela pagamentos)
                cur.execute(
                    """
                    INSERT INTO pagamentos (usuario_id, payment_asaas_id, referencia, valor, evento, creditos_adicionados)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (usuario_id, payment_id, reference, value, evento, creditos),
                )
                conn.commit()
            return {"status": "ok", "creditos_adicionados": creditos}
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ASAAS WEBHOOK] Erro: {e}")
        # Retornar 200 para o Asaas não ficar reenviando; logamos o erro
        return {"status": "ok", "erro": str(e)}
