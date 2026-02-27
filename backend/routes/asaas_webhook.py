from fastapi import APIRouter, Request, HTTPException
import os

try:
    # Quando usado como parte do pacote backend
    from ..database import get_connection
except ImportError:
    # Fallback para execução direta
    from backend.database import get_connection  # type: ignore

router = APIRouter(prefix="/genapi", tags=["asaas"])

# Regra de monetização: R$ 0,25/crédito; +20% acima de 300
PRECO_CREDITO = 0.25
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20


def _calcular_creditos_entregues(quantidade_comprada: int) -> int:
    """creditos_finais = quantidade + bonus (bonus = 20% se quantidade > 300)."""
    bonus = 0
    if quantidade_comprada > BONUS_THRESHOLD:
        bonus = int(quantidade_comprada * BONUS_PERCENT)
    return quantidade_comprada + bonus


def _adicionar_creditos_usuario(usuario_id: int, qtd: int) -> bool:
    """
    Versão local de adicionar_creditos_usuario para evitar dependência/ciclo com api.py.
    Usa a mesma lógica: soma creditos na tabela usuarios.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET creditos = creditos + %s
                WHERE id = %s
                """,
                (qtd, usuario_id),
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ ERRO ao adicionar créditos via webhook Asaas: {e}")
        return False
    finally:
        conn.close()


@router.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    """
    Webhook de pagamento/assinatura do Asaas.
    URL final: POST /genapi/webhook/asaas
    """
    # 🔐 1. Validar token
    token_recebido = request.headers.get("access_token") or request.headers.get("accessToken")
    token_esperado = os.getenv("ASAAS_WEBHOOK_TOKEN")

    if not token_esperado or token_recebido != token_esperado:
        raise HTTPException(status_code=403, detail="Token inválido")

    data = await request.json()

    evento = data.get("event")
    customer_id = None
    valor = None
    reference = None

    # Payload Asaas pode vir com payment ou subscription
    if "payment" in data and data["payment"]:
        customer_id = data["payment"].get("customer")
        valor = data["payment"].get("value")
        reference = data["payment"].get("externalReference")
    elif "subscription" in data and data["subscription"]:
        customer_id = data["subscription"].get("customer")
        valor = data["subscription"].get("value")
        reference = data["subscription"].get("externalReference")
    else:
        return {"status": "ignorado"}

    # 🎯 Só processar eventos relevantes
    if evento not in ["PAYMENT_CONFIRMED", "SUBSCRIPTION_CHARGED"]:
        return {"status": "evento_ignorado"}

    if not customer_id or not reference:
        raise HTTPException(status_code=400, detail="Payload incompleto (customer/reference ausentes)")

    # 🛑 Idempotência básica (evita duplicar crédito)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM pagamentos WHERE referencia = %s", (reference,))
            pagamento_existente = cursor.fetchone()

            if pagamento_existente:
                return {"status": "ja_processado"}

            # 🔎 Buscar usuário pelo asaas_customer_id
            cursor.execute(
                "SELECT id FROM usuarios WHERE asaas_customer_id = %s",
                (customer_id,),
            )
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="Usuário não encontrado para o customer_id informado")

            # Se cursor usa RealDictCursor, user["id"]; se não, user[0]
            user_id = user["id"] if isinstance(user, dict) else user[0]

            # 💰 Créditos: reference no formato pacote_<quantidade> (ex: pacote_150 → comprou 150, recebe 180)
            creditos = 0
            quantidade_comprada = 0

            if reference and reference.startswith("pacote_"):
                try:
                    # pacote_50, pacote_150, etc.
                    quantidade_comprada = int(reference.replace("pacote_", "").strip())
                    creditos = _calcular_creditos_entregues(quantidade_comprada)
                except ValueError:
                    pass
            if creditos <= 0:
                # Fallback: valor em R$ / 0,25 = quantidade comprada
                try:
                    quantidade_comprada = int(round(float(valor) / PRECO_CREDITO))
                    creditos = _calcular_creditos_entregues(quantidade_comprada)
                except Exception:
                    creditos = 0

            if creditos <= 0:
                raise HTTPException(status_code=400, detail="Não foi possível calcular créditos para este pagamento")

            # ➕ Adicionar créditos
            if not _adicionar_creditos_usuario(user_id, creditos):
                raise HTTPException(status_code=500, detail="Falha ao adicionar créditos")

            # 📝 Registrar pagamento (tabela pagamentos deve existir)
            cursor.execute(
                """
                INSERT INTO pagamentos (usuario_id, referencia, valor, evento)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, reference, valor, evento),
            )
            conn.commit()

        return {"status": "credito_adicionado", "creditos": creditos}
    finally:
        conn.close()

