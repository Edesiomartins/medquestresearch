import psycopg2  # pyright: ignore[reportMissingModuleSource]
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
# Carregar variáveis de ambiente
load_dotenv()

# ============================================================
# ✅ CONFIGURAÇÃO DO BANCO (via variáveis de ambiente)
# ============================================================
# IMPORTANTE: O Railway fornece DATABASE_URL automaticamente
# ou configure manualmente no Railway Dashboard

# Tentar usar DATABASE_URL primeiro (formato do Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Parse da URL do PostgreSQL (formato: postgresql://user:password@host:port/dbname)
    parsed = urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname
    DB_USER = parsed.username
    DB_PASS = parsed.password
    DB_NAME = parsed.path.lstrip('/')
    DB_PORT = parsed.port or 5432
else:
    # Fallback para variáveis individuais
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Validar que todas as variáveis estão configuradas
# Se DATABASE_URL não estiver configurado, verificar variáveis individuais
if not DATABASE_URL and not all([DB_HOST, DB_USER, DB_PASS, DB_NAME]):
    missing = []
    if not DB_HOST:
        missing.append("DB_HOST")
    if not DB_USER:
        missing.append("DB_USER")
    if not DB_PASS:
        missing.append("DB_PASSWORD")
    if not DB_NAME:
        missing.append("DB_NAME")
    
        raise ValueError(
            f"❌ Variáveis de ambiente do banco de dados não configuradas: {', '.join(missing)}\n"
            f"Configure DATABASE_URL no Railway Dashboard: Variables\n"
            f"Ou configure individualmente: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
        )


# ============================================================
# ✅ CRIAR CONEXÃO GLOBAL (reuso recomendado)
# ============================================================

def get_connection(autocommit=True):
    """
    Cria conexão com o banco de dados PostgreSQL.
    Por padrão usa autocommit=True para compatibilidade.
    Para threads com commit explícito, use autocommit=False.
    """
    try:
        # Usar DATABASE_URL se disponível, senão usar variáveis individuais
        if DATABASE_URL:
            conn = psycopg2.connect(
                DATABASE_URL,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        else:
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                port=DB_PORT,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        
        # PostgreSQL não tem autocommit por padrão
        if autocommit:
            conn.autocommit = True
        
        return conn
    except Exception as e:
        print("❌ ERRO ao conectar no PostgreSQL (MedQuestResearch):", e)
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
