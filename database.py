import pymysql
import pymysql.cursors

# ============================================================
# ✅ CONFIGURAÇÃO FIXA DO BANCO (MedQuestGen)
# ============================================================

DB_HOST = "dredesiomartins.mysql.pythonanywhere-services.com"
DB_USER = "dredesiomartins"
DB_PASS = "Minhavida.25"
DB_NAME = "dredesiomartins$MedquestGen"


# ============================================================
# ✅ CRIAR CONEXÃO GLOBAL (reuso recomendado no PythonAnywhere)
# ============================================================

def get_connection():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
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
    """Executa INSERT/UPDATE/DELETE."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return True
    except Exception as e:
        print("❌ ERRO ao executar comando SQL:", e)
        return False
    finally:
        conn.close()
