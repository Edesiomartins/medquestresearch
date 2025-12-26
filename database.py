import pymysql
import pymysql.cursors
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ============================================================
# ✅ CONFIGURAÇÃO DO BANCO (via variáveis de ambiente)
# ============================================================

DB_HOST = os.getenv("DB_HOST", "dredesiomartins.mysql.pythonanywhere-services.com")
DB_USER = os.getenv("DB_USER", "dredesiomartins")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "dredesiomartins$MedquestResearch")


# ============================================================
# ✅ CRIAR CONEXÃO GLOBAL (reuso recomendado no PythonAnywhere)
# ============================================================

def get_connection(autocommit=True):
    """
    Cria conexão com o banco de dados.
    Por padrão usa autocommit=True para compatibilidade.
    Para threads com commit explícito, use autocommit=False.
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=autocommit
        )
        return conn
    except Exception as e:
        print("❌ ERRO ao conectar no MySQL (MedQuestGen):", e)
        raise


# ============================================================
# ✅ FUNÇÕES UTILITÁRIAS DE BANCO
# ============================================================

def db_select(query, params=None):
    """Executa SELECT e retorna múltiplos resultados."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        conn.close()


def db_select_one(query, params=None):
    """Executa SELECT e retorna somente uma linha."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()


def db_execute(query, params=None):
    """Executa INSERT/UPDATE/DELETE e retorna rowcount."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount
    except Exception as e:
        print("❌ ERRO ao executar comando SQL:", e)
        return 0
    finally:
        conn.close()
