"""
Serviço central de créditos: consumo por módulo e histórico para auditoria/dashboard.
"""

from fastapi import HTTPException

try:
    from backend.database import get_connection
except ImportError:
    try:
        from database import get_connection
    except ImportError:
        from ..database import get_connection

# Custos por módulo (créditos por unidade)
CUSTOS = {
    "pdf": 5,
    "explicar": 10,
    "fatos": 5,
    "critica": 12,
    "perspectiva": 15,
    "meta_etapa": 15,
    "meta_upload": 5,
    "mapa": 8,
    "structure_mapper": 6,
    "meta_analise": 12,
    "chat_followup": 1,
}


def _custo_modulo(modulo: str, quantidade: int = 1) -> int:
    """Retorna custo total para o módulo (custo_unitario * quantidade)."""
    m = modulo.lower()
    if m not in CUSTOS:
        # Aliases
        alias = {
            "critical_analysis": "critica",
            "fact_checker": "fatos",
            "perspective_research": "perspectiva",
            "structure_visualizer": "mapa",
            "meta_analysis": "meta_analise",
        }
        m = alias.get(m, m)
    if m not in CUSTOS:
        raise HTTPException(status_code=400, detail=f"Módulo inválido: {modulo}")
    return CUSTOS[m] * max(1, quantidade)


def consumir_creditos(usuario_id: int, modulo: str, quantidade: int = 1) -> int:
    """
    Debita créditos do usuário e registra no histórico.
    Usa creditos_usados (disponível = creditos - creditos_usados).
    """
    custo_total = _custo_modulo(modulo, quantidade)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT creditos, creditos_usados FROM usuarios WHERE id = %s",
                (usuario_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            creditos = row.get("creditos", 0) or 0
            creditos_usados = row.get("creditos_usados", 0) or 0
            disponivel = creditos - creditos_usados
            if disponivel < custo_total:
                raise HTTPException(
                    status_code=402,
                    detail=f"Créditos insuficientes. Necessário: {custo_total}, disponível: {disponivel}",
                )
            cur.execute(
                "UPDATE usuarios SET creditos_usados = creditos_usados + %s WHERE id = %s",
                (custo_total, usuario_id),
            )
            cur.execute(
                """
                INSERT INTO historico_creditos
                (usuario_id, tipo, modulo, quantidade, custo_total)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (usuario_id, "consumo", modulo, quantidade, custo_total),
            )
        conn.commit()
        return custo_total
    finally:
        conn.close()


def consumir_creditos_total(usuario_id: int, custo_total: int, modulo: str) -> int:
    """
    Debita um valor fixo de créditos e registra no histórico (ex.: upload N arquivos + análise).
    """
    if custo_total <= 0:
        return 0
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT creditos, creditos_usados FROM usuarios WHERE id = %s",
                (usuario_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            creditos = row.get("creditos", 0) or 0
            creditos_usados = row.get("creditos_usados", 0) or 0
            disponivel = creditos - creditos_usados
            if disponivel < custo_total:
                raise HTTPException(
                    status_code=402,
                    detail=f"Créditos insuficientes. Necessário: {custo_total}, disponível: {disponivel}",
                )
            cur.execute(
                "UPDATE usuarios SET creditos_usados = creditos_usados + %s WHERE id = %s",
                (custo_total, usuario_id),
            )
            cur.execute(
                """
                INSERT INTO historico_creditos (usuario_id, tipo, modulo, quantidade, custo_total)
                VALUES (%s, 'consumo', %s, 1, %s)
                """,
                (usuario_id, modulo, custo_total),
            )
        conn.commit()
        return custo_total
    finally:
        conn.close()


def registrar_compra(usuario_id: int, quantidade: int, custo_total: int = 0) -> None:
    """Registra compra de créditos no histórico (chamado pelo webhook ao creditar)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO historico_creditos (usuario_id, tipo, modulo, quantidade, custo_total)
                VALUES (%s, 'compra', NULL, %s, %s)
                """,
                (usuario_id, quantidade, custo_total),
            )
        conn.commit()
    finally:
        conn.close()
