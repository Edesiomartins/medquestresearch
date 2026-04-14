# ============================================
# ? IMPORTS E CONFIGURA??ES INICIAIS
# ============================================

import sys
import os
import hashlib
import secrets
import datetime
import time
import logging
import threading
import traceback
import json
import math
try:
    import bcrypt
except ImportError:
    bcrypt = None
from functools import wraps
from psycopg2 import IntegrityError

# Carregar vari?veis de ambiente do arquivo .env (local). Em produ??o/Railway as vars v?m do ambiente.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logging.info(f"[ENV] .env carregado de: {env_path}")
    else:
        load_dotenv()  # tenta diret?rio atual; em produ??o n?o existe .env e est? ok
except ImportError:
    pass  # python-dotenv opcional em produ??o
except Exception as e:
    logging.debug(f"[ENV] Erro ao carregar .env: {e}")

from fastapi import FastAPI, Request, HTTPException, Depends, Header, File, UploadFile, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler  # pyright: ignore[reportMissingImports]
from slowapi.util import get_remote_address  # pyright: ignore[reportMissingImports]
from slowapi.errors import RateLimitExceeded  # pyright: ignore[reportMissingImports]  # pyright: ignore[reportMissingImports]
from slowapi.middleware import SlowAPIMiddleware  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel, validator
from typing import Optional

from docx import Document  # pyright: ignore[reportMissingImports]

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================
# ? AJUSTAR IMPORTA??ES PARA FUNCIONAR TANTO NA RAIZ QUANTO EM backend/
# ============================================

# Banco de dados - tentar relativo primeiro, depois absoluto
# Se estiver em backend/, adicionar o diret?rio ao path para importa??es absolutas funcionarem
_parent_dir = os.path.dirname(BASE_DIR)
if _parent_dir not in sys.path and os.path.basename(BASE_DIR) == "backend":
    sys.path.insert(0, _parent_dir)
    # Tamb?m adicionar backend/ ao path
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

try:
    from .database import db_select, db_select_one, db_execute, get_connection
except ImportError:
    try:
        import database
        db_select = database.db_select
        db_select_one = database.db_select_one
        db_execute = database.db_execute
        get_connection = database.get_connection
    except ImportError:
        # ?ltima tentativa: importar do backend
        import backend.database as database  # type: ignore[reportMissingImports]
        db_select = database.db_select
        db_select_one = database.db_select_one
        db_execute = database.db_execute
        get_connection = database.get_connection

try:
    from .critical_analysis import aplicar_leitura_critica
except ImportError:
    try:
        import critical_analysis
        aplicar_leitura_critica = critical_analysis.aplicar_leitura_critica
    except ImportError:
        import backend.critical_analysis as critical_analysis  # pyright: ignore[reportMissingImports]
        aplicar_leitura_critica = critical_analysis.aplicar_leitura_critica

try:
    from .pdf_processor import extrair_texto_pdf, obter_versao_portugues
except ImportError:
    try:
        import pdf_processor
        extrair_texto_pdf = pdf_processor.extrair_texto_pdf
        obter_versao_portugues = pdf_processor.obter_versao_portugues
    except ImportError:
        import backend.pdf_processor as pdf_processor  # type: ignore[reportMissingImports]
        extrair_texto_pdf = pdf_processor.extrair_texto_pdf
        obter_versao_portugues = pdf_processor.obter_versao_portugues

try:
    from .meta_analysis import gerar_meta_analise, escrever_secao_artigo
except ImportError:
    try:
        import meta_analysis
        gerar_meta_analise = meta_analysis.gerar_meta_analise
        escrever_secao_artigo = meta_analysis.escrever_secao_artigo
    except ImportError:
        import backend.meta_analysis as meta_analysis  # type: ignore[reportMissingImports]
        gerar_meta_analise = meta_analysis.gerar_meta_analise
        escrever_secao_artigo = meta_analysis.escrever_secao_artigo

try:
    from .credit_costs import get_credit_cost, get_all_costs
except ImportError:
    try:
        import credit_costs
        get_credit_cost = credit_costs.get_credit_cost
        get_all_costs = credit_costs.get_all_costs
    except ImportError:
        import backend.credit_costs as credit_costs  # type: ignore[reportMissingImports]
        get_credit_cost = credit_costs.get_credit_cost
        get_all_costs = credit_costs.get_all_costs

try:
    from .services.credit_service import consumir_creditos, consumir_creditos_total, registrar_compra
except ImportError:
    try:
        from services.credit_service import consumir_creditos, consumir_creditos_total, registrar_compra
    except ImportError:
        import backend.services.credit_service as credit_service  # type: ignore[reportMissingImports]
        consumir_creditos = credit_service.consumir_creditos
        consumir_creditos_total = credit_service.consumir_creditos_total
        registrar_compra = credit_service.registrar_compra

try:
    from .services.evidence_graph_service import (
        build_graph_from_extraction_json,
        upsert_project_evidence_graph,
    )
except ImportError:
    try:
        from services.evidence_graph_service import (
            build_graph_from_extraction_json,
            upsert_project_evidence_graph,
        )
    except ImportError:
        import backend.services.evidence_graph_service as evidence_graph_service  # type: ignore[reportMissingImports]
        build_graph_from_extraction_json = evidence_graph_service.build_graph_from_extraction_json
        upsert_project_evidence_graph = evidence_graph_service.upsert_project_evidence_graph

try:
    from .cache_llm import limpar_cache_antigo
except ImportError:
    try:
        from cache_llm import limpar_cache_antigo
    except ImportError:
        try:
            import backend.cache_llm as cache_llm  # type: ignore[reportMissingImports]
            limpar_cache_antigo = cache_llm.limpar_cache_antigo
        except Exception:
            limpar_cache_antigo = None

# ============================================
# ? APLICA??O FASTAPI
# ============================================

app = FastAPI(title="MedQuestResearch API", version="2.0")

if bcrypt is None:
    logging.warning("[SECURITY] bcrypt não está instalado; usando fallback legado com SHA256. Instale bcrypt no ambiente de produção.")

# ? ROUTER COM PREFIXO /genapi PARA TODAS AS ROTAS DE API
api_router = APIRouter(prefix="/genapi")

# ? Configura??o de rate limiting (adicionar primeiro)
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ? CONFIGURA??O CORS CORRETA E SIMPLES (adicionar por ?ltimo para executar primeiro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://medquestresearch.up.railway.app",
    ],
    allow_credentials=False,   # ?? IMPORTANTE: voc? usa token no header, n?o cookie
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def recover_stuck_jobs_on_startup():
    """
    Na inicialização, marca jobs antigos em processing como failed e
    garante coluna started_at para controle de timeout.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            tempo_base_col = "created_at"
            try:
                cur.execute(
                    """
                    ALTER TABLE research_jobs
                    ADD COLUMN IF NOT EXISTS started_at TIMESTAMP
                    """
                )
            except Exception as e:
                logging.warning(f"[STARTUP] Não foi possível garantir coluna started_at: {e}")

            try:
                cur.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'research_jobs'
                      AND column_name IN ('created_at', 'criado_em')
                    """
                )
                cols = [r.get("column_name") for r in (cur.fetchall() or [])]
                if "created_at" in cols:
                    tempo_base_col = "created_at"
                elif "criado_em" in cols:
                    tempo_base_col = "criado_em"
                else:
                    tempo_base_col = "created_at"
            except Exception:
                tempo_base_col = "created_at"

            cur.execute(
                f"""
                UPDATE research_jobs
                SET started_at = COALESCE(started_at, {tempo_base_col}, NOW())
                WHERE status = 'processing' AND started_at IS NULL
                """
            )

            cur.execute(
                f"""
                UPDATE research_jobs
                SET status = 'failed',
                    erro = COALESCE(erro, 'Processamento interrompido por reinicialização do servidor. Tente novamente.'),
                    resultado = COALESCE(resultado, 'Processamento interrompido por reinicialização do servidor. Tente novamente.')
                WHERE status = 'processing'
                  AND COALESCE(started_at, {tempo_base_col}) < NOW() - INTERVAL '10 minutes'
                """
            )
        conn.commit()
    except Exception as e:
        logging.error(f"[STARTUP] Falha ao recuperar jobs travados: {e}")
    finally:
        conn.close()

    try:
        if callable(limpar_cache_antigo):
            limpar_cache_antigo()
    except Exception as e:
        logging.warning(f"[STARTUP] Falha ao limpar cache LLM antigo: {e}")

# ============================================
# ? MODELOS PYDANTIC
# ============================================

class CadastroInput(BaseModel):
    nome: str
    email: str
    senha: str

class LoginRequest(BaseModel):
    email: str
    senha: str


class AtualizarPerfilInput(BaseModel):
    """Campos opcionais para atualizar cadastro (perfil)."""
    nome: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None


# ============================================
# ? FUN??ES AUXILIARES
# ============================================

def gerar_token():
    return secrets.token_hex(32)

def hash_senha(senha):
    # Fallback para manter app funcional caso bcrypt não esteja disponível no ambiente.
    if bcrypt is None:
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _is_sha256_legacy(hash_armazenado: str) -> bool:
    if not hash_armazenado or len(hash_armazenado) != 64:
        return False
    return all(c in "0123456789abcdef" for c in hash_armazenado.lower())


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    if _is_sha256_legacy(hash_armazenado):
        return hashlib.sha256(senha.encode("utf-8")).hexdigest() == hash_armazenado
    if bcrypt is None:
        # Sem bcrypt instalado, não é possível validar hash bcrypt.
        return False
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
    except Exception:
        return False

def gerar_hash_senha(senha):
    return hash_senha(senha)

def creditos_disponiveis(usuario):
    return max(0, usuario["creditos"] - usuario["creditos_usados"])

def adicionar_creditos_usuario(usuario_id, qtd):
    """Adiciona creditos a um usuario."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios
                SET creditos = creditos + %s
                WHERE id = %s
            """, (qtd, usuario_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"? ERRO ao adicionar cr?ditos: {e}")
        return False
    finally:
        conn.close()

def debitar_creditos(usuario_id, qtd):
    """Debita creditos apenas se houver creditos disponiveis suficientes."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios
                SET creditos_usados = creditos_usados + %s
                WHERE id = %s AND (creditos - creditos_usados) >= %s
            """, (qtd, usuario_id, qtd))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"? ERRO ao debitar cr?ditos: {e}")
        return False
    finally:
        conn.close()

def db_insert_return_id(sql, params):
    """Executa um INSERT e retorna o ID do registro inserido."""
    # Para PostgreSQL, precisamos usar RETURNING id
    if "RETURNING" not in sql.upper():
        sql = sql.rstrip(";") + " RETURNING id"
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            conn.commit()
            return result["id"] if result else None
    finally:
        conn.close()

def registrar_log(usuario_id, modulo, entrada, saida, creditos, request: Request = None):
    ip = request.client.host if request and request.client else "unknown"
    db_execute("""
        INSERT INTO gen_logs_uso (usuario_id, modulo, entrada, saida, creditos_gastos, ip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, modulo, entrada, saida, creditos, ip))

def read_docx(file_path):
    """L? o conte?do de um arquivo DOCX e retorna como string."""
    doc = Document(file_path)
    text = '\n'.join([p.text for p in doc.paragraphs])
    return text

def get_current_user(authorization: str = Header(None)):
    """Autentica??o: extrai token do header (Bearer ou puro) e busca usu?rio no banco."""
    if not authorization:
        raise HTTPException(status_code=401, detail="N?o autorizado")
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()
    if not token:
        raise HTTPException(status_code=401, detail="N?o autorizado")
    row = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not row:
        raise HTTPException(status_code=401, detail="N?o autorizado")
    return dict(row)

def require_api_key(authorization: str = Header(None)):
    """Dependency para autentica??o em rotas FastAPI."""
    return get_current_user(authorization)


ADMIN_EMAIL = "prof.edesio@gmail.com"


def require_admin(authorization: str = Header(None)):
    """Dependency: apenas usu?rio admin (prof.edesio@gmail.com) pode acessar."""
    user = get_current_user(authorization)
    email = (user.get("email") or "").strip().lower()
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador.")
    return user

# ============================================
# ? FUN??ES DE PROCESSAMENTO ASS?NCRONO
# ============================================

def processar_job_critica(job_id: int, texto_artigo: str, foco_analise: str = "geral"):
    """Processa job de an?lise cr?tica em background - SEM chunking para an?lise focada."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] in?cio - critica (foco: {foco_analise})")
        
        # Limitar texto drasticamente para an?lise focada (sem chunking)
        texto_artigo = texto_artigo[:3000]  # Reduzido de 4000 para 3000
        
        # Chamada direta SEM chunking - an?lise focada ? mais r?pida
        resultado = aplicar_leitura_critica(texto_artigo, foco_analise)
        
        # Usar conex?o expl?cita com commit expl?cito para garantir funcionamento em threads
        # autocommit=False para permitir controle expl?cito do commit
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit expl?cito na mesma conex?o
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE conclu?do - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] conclu?do - critica")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - critica\n{erro}")
        
        # Usar conex?o expl?cita com commit expl?cito para garantir funcionamento em threads
        # autocommit=False para permitir controle expl?cito do commit
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit expl?cito na mesma conex?o
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def _extrair_json_do_texto(texto: str):
    """Tenta extrair um objeto JSON do texto (bloco ```json ... ``` ou primeiro {...})."""
    if not texto or not texto.strip():
        return None
    texto = texto.strip()
    # Bloco ```json ... ```
    for marker in ("```json", "```"):
        i = texto.find(marker)
        if i >= 0:
            fim = texto.find("```", i + len(marker))
            if fim > i:
                bloco = texto[i + len(marker):fim].strip()
                try:
                    return json.loads(bloco)
                except Exception:
                    pass
    # Primeiro { at? ?ltimo }
    inicio = texto.find("{")
    if inicio >= 0:
        fim = texto.rfind("}")
        if fim > inicio:
            try:
                return json.loads(texto[inicio:fim + 1])
            except Exception:
                pass
    return None


def processar_job_meta_analise(job_id: int, tema: str, etapa: str = "1", texto_artigo: str = None, dados_extras: dict = None):
    """Processa job de metan?lise em background. Fluxo: Etapa 2 ? confirma??o humana ? Evidence Graph ? Etapa 3 ? 4 ? 5."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] in?cio - meta_analise (etapa: {etapa}, tema: {tema})")

        # Limitar texto se fornecido
        if texto_artigo:
            texto_artigo = texto_artigo[:6000]

        # Chamar fun??o de metan?lise (agora retorna dict com 'resultado' e 'artigos')
        resultado_dict = gerar_meta_analise(tema=tema, etapa=etapa, texto_artigo=texto_artigo, dados_extras=dados_extras)

        resultado_texto = resultado_dict.get('resultado', '')
        artigos_encontrados = resultado_dict.get('artigos', [])
        total_artigos = resultado_dict.get('total_artigos', 0)

        # Preparar dados extras com artigos (se houver)
        dados_extras_atualizados = dados_extras.copy() if dados_extras else {}
        if artigos_encontrados:
            dados_extras_atualizados['artigos'] = artigos_encontrados
            dados_extras_atualizados['total_artigos'] = total_artigos

        # Etapa 2: persistir extraction_json em dados_extras e atualizar Evidence Graph incremental
        parsed = None
        if etapa == "2" and resultado_texto:
            parsed = _extrair_json_do_texto(resultado_texto)
            if isinstance(parsed, dict) and (parsed.get("study_metadata") or parsed.get("outcomes")):
                dados_extras_atualizados["extraction_json"] = parsed

        # Usar conex?o expl?cita com commit expl?cito para garantir funcionamento em threads
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                dados_extras_json = json.dumps(dados_extras_atualizados) if dados_extras_atualizados else None
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s, dados_extras=%s WHERE id=%s",
                    ("done", resultado_texto, dados_extras_json, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE conclu?do - job_id={job_id}, linhas_afetadas={rowcount}, artigos={len(artigos_encontrados)}")

            # Etapa 2: ao terminar, disparar build do graph e salvar por project_id (incremental)
            if etapa == "2" and parsed and (dados_extras or {}).get("project_id") is not None and (dados_extras or {}).get("usuario_id") is not None:
                try:
                    project_id = int((dados_extras or {})["project_id"])
                    usuario_id = int((dados_extras or {})["usuario_id"])
                    meta = parsed.get("study_metadata") or {}
                    titulo_artigo = (meta.get("title") or meta.get("authors") or f"Estudo {job_id}").strip()[:100]
                    year = meta.get("year") or ""
                    study_label = f"{titulo_artigo} {year}".strip() or f"Estudo {job_id}"
                    graph = build_graph_from_extraction_json(parsed, study_label=study_label, study_id=job_id)
                    upsert_project_evidence_graph(conn, project_id, usuario_id, graph)
                    logging.warning(f"[RESEARCH JOB {job_id}] Evidence Graph atualizado (project_id={project_id})")
                except Exception as e_eg:
                    logging.warning(f"[RESEARCH JOB {job_id}] Evidence Graph (n?o bloqueante): {e_eg}")
        finally:
            conn.close()

        logging.warning(f"[RESEARCH JOB {job_id}] conclu?do - meta_analise")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - meta_analise\n{erro}")
        
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

# ============================================
# ? MODELOS PYDANTIC PARA VALIDA??O
# ============================================

class InputCritica(BaseModel):
    texto_artigo: str
    foco_analise: Optional[str] = "geral"  # M?todo de an?lise cr?tica escolhido

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo n?o pode estar vazio")
        return v

class InputMetaAnalise(BaseModel):
    tema: Optional[str] = ""  # Tema agora ? opcional (novo fluxo usa upload de artigos)
    etapa: Optional[str] = "1"  # 1=PICO+Busca, 2=Extra??o, 3=PRISMA/qualidade, 4=Sele??o final, 5=Metan?lise
    texto_artigo: Optional[str] = None  # Opcional - usado apenas nas etapas 2-4
    json_extracao: Optional[str] = None
    estilo: Optional[str] = "Vancouver"  # Vancouver ou ABNT
    manuscrito: Optional[str] = None
    artigos_analisados: Optional[str] = None  # JSON string com artigos analisados (novo fluxo)
    project_id: Optional[int] = None  # Agrupa jobs para Evidence Graph (ap?s confirma??o humana, antes Etapa 3)


class EscreverArtigoRequest(BaseModel):
    project_id: int
    tema: str
    secao: str = "completo"  # resumo|introducao|metodos|resultados|discussao|completo
    estilo_referencia: str = "Vancouver"
    idioma: str = "pt"
    instrucoes_adicionais: str = ""

# ============================================
# ? HANDLER DE ERROS GLOBAL
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exce??es."""
    import traceback
    error_detail = str(exc)
    logging.error(f"Erro global: {error_detail}\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={"erro": error_detail}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handler para erros 404."""
    return JSONResponse(
        status_code=404,
        content={
            "erro": "Rota n?o encontrada",
            "path": str(request.url.path),
            "message": "Verifique se a rota est? correta e se o servidor est? rodando"
        }
    )

# ============================================
# ? ROTAS B?SICAS
# ============================================


@app.get("/")
def index():
    return {"status": "Medquestresearch API est? ativa ?", "version": "2.0"}

@app.get("/ping")
def ping():
    return {"message": "pong", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/db-test")
def db_test():
    try:
        r = db_select_one("SELECT count(*) AS total FROM usuarios")
        return {"ok": True, "usuarios": r["total"]}
    except Exception as e:
        return {"ok": False, "erro": str(e)}

@app.get("/cors-test")
def cors_test():
    """Rota de teste para verificar se CORS est? funcionando"""
    return {
        "status": "CORS Test",
        "message": "Se voc? v? esta mensagem, CORS est? funcionando!",
        "timestamp": datetime.datetime.now().isoformat()
    }

@api_router.get("/test-db")
def test_db():
    """Rota de teste para verificar se o banco de dados est? acess?vel"""
    try:
        if not os.getenv("DATABASE_URL"):
            return {
                "ok": False,
                "erro": "DATABASE_URL n?o configurada",
                "dica": "Configure a vari?vel DATABASE_URL no ambiente (Railway ou .env)"
            }
        
        r = db_select_one("SELECT count(*) AS total FROM usuarios")
        return {
            "ok": True,
            "usuarios": r["total"],
            "message": "Banco de dados est? acess?vel!"
        }
    except Exception as e:
        return {
            "ok": False,
            "erro": str(e),
            "tipo": type(e).__name__
        }

# ============================================
# ? ROTAS DE ADMINISTRA??O (CR?DITOS)
# ============================================

class AdicionarCreditosInput(BaseModel):
    usuario_id: Optional[int] = None
    email: Optional[str] = None
    quantidade: int

    @validator('quantidade')
    def validate_quantidade(cls, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v

    @validator('email')
    def validate_email_ou_id(cls, v, values):
        if not values.get('usuario_id') and not v:
            raise ValueError("Deve fornecer usuario_id ou email")
        return v

class ChatFollowUpInput(BaseModel):
    tipo_analise: str
    texto_artigo: Optional[str] = None
    mensagem: str
    historico: Optional[list] = None

@api_router.get("/admin/custos")
@limiter.limit("20 per minute")
def listar_custos(request: Request, user = Depends(require_api_key)):
    """
    Lista todos os custos configurados para cada tipo de requisi??o.
    Requer autentica??o de administrador.
    """
    try:
        custos = get_all_costs()
        return {
            "custos": custos,
            "total_modulos": len(custos),
            "observacao": "Valores podem ser ajustados via vari?veis de ambiente CREDIT_COST_<MODULO>"
        }
    except Exception as e:
        logging.error(f"Erro ao listar custos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar custos: {str(e)}")


@api_router.get("/admin/metricas-creditos")
@limiter.limit("30 per minute")
def metricas_creditos(request: Request, user=Depends(require_admin)):
    """
    Dashboard de m?tricas de cr?ditos: auditoria, uso por m?dulo, compras.
    Acesso restrito ao admin (prof.edesio@gmail.com).
    """
    try:
        # Totais por tipo
        totais_tipo = db_select(
            """
            SELECT tipo, COUNT(*) AS qtd, COALESCE(SUM(custo_total), 0)::bigint AS total_creditos
            FROM historico_creditos
            GROUP BY tipo
            """
        )
        compras = next((t for t in totais_tipo if t.get("tipo") == "compra"), {})
        consumo = next((t for t in totais_tipo if t.get("tipo") == "consumo"), {})

        # Uso por m?dulo (consumo)
        por_modulo = db_select(
            """
            SELECT modulo, COUNT(*) AS qtd_registros, COALESCE(SUM(custo_total), 0)::bigint AS total_creditos
            FROM historico_creditos
            WHERE tipo = 'consumo' AND modulo IS NOT NULL
            GROUP BY modulo
            ORDER BY total_creditos DESC
            """
        )

        # ?ltimos 50 registros (auditoria)
        ultimos = db_select(
            """
            SELECT h.id, h.usuario_id, u.email, u.nome, h.tipo, h.modulo, h.quantidade, h.custo_total, h.criado_em
            FROM historico_creditos h
            LEFT JOIN usuarios u ON u.id = h.usuario_id
            ORDER BY h.criado_em DESC
            LIMIT 50
            """
        )
        for r in ultimos:
            if r.get("criado_em"):
                r["criado_em"] = r["criado_em"].isoformat() if hasattr(r["criado_em"], "isoformat") else str(r["criado_em"])

        return {
            "resumo": {
                "compras": {"registros": compras.get("qtd", 0), "total_creditos": compras.get("total_creditos", 0)},
                "consumo": {"registros": consumo.get("qtd", 0), "total_creditos": consumo.get("total_creditos", 0)},
            },
            "por_modulo": list(por_modulo),
            "ultimos_registros": list(ultimos),
        }
    except Exception as e:
        logging.exception("Erro em metricas_creditos: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/adicionar-creditos")
@limiter.limit("20 per minute")
def adicionar_creditos(request: Request, data: AdicionarCreditosInput, user = Depends(require_api_key)):
    """
    Adiciona creditos a um usuario.
    Pode ser identificado por ID ou email.
    """
    try:
        # Buscar usu?rio por ID ou email
        if data.usuario_id:
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE id = %s", (data.usuario_id,))
        elif data.email:
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE email = %s", (data.email,))
        else:
            raise HTTPException(status_code=400, detail="Deve fornecer usuario_id ou email")

        if not usuario:
            raise HTTPException(status_code=404, detail="Usu?rio n?o encontrado")

        # Adicionar creditos usando funcao auxiliar
        if not adicionar_creditos_usuario(usuario["id"], data.quantidade):
            raise HTTPException(status_code=500, detail="Erro ao atualizar creditos no banco de dados")

        # Buscar dados atualizados
        usuario_atualizado = db_select_one(
            "SELECT id, nome, email, creditos, creditos_usados FROM usuarios WHERE id = %s",
            (usuario["id"],)
        )

        return {
            "mensagem": "Creditos adicionados com sucesso",
            "usuario": {
                "id": usuario_atualizado["id"],
                "nome": usuario_atualizado["nome"],
                "email": usuario_atualizado["email"],
                "creditos_anteriores": usuario["creditos"],
                "creditos_adicionados": data.quantidade,
                "creditos_atuais": usuario_atualizado["creditos"],
                "creditos_usados": usuario_atualizado.get("creditos_usados", 0),
                "creditos_disponiveis": usuario_atualizado["creditos"] - usuario_atualizado.get("creditos_usados", 0)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro ao adicionar cr?ditos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar cr?ditos: {str(e)}")

@app.get("/routes")
def list_routes():
    """Lista todas as rotas registradas para debug."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, "name", "N/A")
            })
    return {
        "total_routes": len(routes),
        "routes": routes,
        "api_router_included": any("/genapi" in r["path"] for r in routes)
    }

# ============================================
# ? ROTAS DE USU?RIO
# ============================================

@api_router.get("/test")
def test_router():
    """Rota de teste para verificar se o router est? funcionando."""
    return {"status": "Router funcionando", "prefix": "/genapi"}

@api_router.post("/cadastro")
def cadastro(request: Request, data: CadastroInput):
    try:
        senha_hash = gerar_hash_senha(data.senha)

        db_execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
            """,
            (data.nome, data.email, senha_hash)
        )

        # Buscar usu?rio criado, gerar token e retornar (login autom?tico p?s-cadastro)
        row = db_select_one("SELECT id, nome, email, creditos, creditos_usados FROM usuarios WHERE email=%s", (data.email,))
        if not row:
            return JSONResponse(status_code=500, content={"erro": "Erro ao criar usu?rio"})

        token = gerar_token()
        db_execute("UPDATE usuarios SET token=%s WHERE id=%s", (token, row["id"]))

        creditos = row.get("creditos", 0) or 0
        creditos_usados = row.get("creditos_usados", 0) or 0
        creditos_disponiveis = max(0, creditos - creditos_usados)

        return {
            "token": token,
            "usuario": {"id": row["id"], "nome": row["nome"], "email": row["email"]},
            "creditos": creditos,
            "creditos_usados": creditos_usados,
            "creditos_disponiveis": creditos_disponiveis,
            "mensagem": "Usu?rio criado com sucesso"
        }

    except IntegrityError:
        return JSONResponse(
            status_code=400,
            content={"erro": "Email j? cadastrado"}
        )

    except Exception as e:
        print("? ERRO NO CADASTRO:")
        print(traceback.format_exc())  # ?? ISSO MOSTRA O ERRO NO LOG

        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
        )

@api_router.post("/login")
@limiter.limit("5 per minute")
def login(request: Request, data: LoginRequest):
    try:
        # Verificar se o banco de dados est? configurado
        if not os.getenv("DATABASE_URL"):
            logging.error("DATABASE_URL n?o configurada")
            raise HTTPException(
                status_code=503,
                detail="Banco de dados n?o configurado. Configure DATABASE_URL no ambiente."
            )
        
        row = db_select_one("SELECT * FROM usuarios WHERE email=%s", (data.email,))
        if not row:
            raise HTTPException(status_code=404, detail="Email n?o encontrado")

        senha_hash = row.get("senha_hash", "")
        if not verificar_senha(data.senha, senha_hash):
            raise HTTPException(status_code=401, detail="Senha incorreta")

        # Migração transparente: hash legado SHA256 -> bcrypt no login bem-sucedido
        if _is_sha256_legacy(senha_hash):
            novo_hash = hash_senha(data.senha)
            db_execute("UPDATE usuarios SET senha_hash=%s WHERE id=%s", (novo_hash, row["id"]))

        token = gerar_token()
        db_execute("UPDATE usuarios SET token=%s WHERE id=%s", (token, row["id"]))

        creditos = row.get("creditos", 0) or 0
        creditos_usados = row.get("creditos_usados", 0) or 0
        creditos_disponiveis = max(0, creditos - creditos_usados)

        return {
            "token": token,
            "usuario": {"id": row["id"], "nome": row["nome"], "email": row["email"]},
            "creditos": creditos,
            "creditos_usados": creditos_usados,
            "creditos_disponiveis": creditos_disponiveis,
            "status": "Login realizado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

# ============================================
# Monetização: apenas compra de créditos
# Preço base histórico R$ 0,25/crédito; reajuste +20% arredondado para cima => R$ 0,30/crédito
# +20% de bônus em créditos acima de 300 unidades compradas
# ============================================

PRECO_CREDITO = math.ceil(0.25 * 1.2 * 100) / 100  # 0.30
BONUS_THRESHOLD = 300
BONUS_PERCENT = 0.20


def calcular_creditos_entregues(quantidade_comprada: int) -> int:
    """
    creditos_finais = quantidade + bonus (bonus = 20% se quantidade > 300).
    """
    bonus = 0
    if quantidade_comprada > BONUS_THRESHOLD:
        bonus = int(quantidade_comprada * BONUS_PERCENT)
    return quantidade_comprada + bonus


def calcular_preco_reais(quantidade_comprada: int) -> float:
    """Preço em R$: valor = quantidade * PRECO_CREDITO."""
    return round(quantidade_comprada * PRECO_CREDITO, 2)


@api_router.get("/planos")
@limiter.limit("30 per minute")
def listar_planos(request: Request):
    """
    Monetização é apenas compra de créditos; não há planos de assinatura.
    Retorna lista vazia para compatibilidade com o frontend.
    """
    return {"planos": [], "mensagem": "Monetização apenas por compra de créditos. Use GET /pacotes."}


@api_router.get("/pacotes")
@limiter.limit("30 per minute")
def listar_pacotes(request: Request):
    """
    Lista pacotes de créditos: preço unitário PRECO_CREDITO; bônus acima de 300 créditos comprados.
    """
    sugestoes = [
        {"id": "50", "nome": "50 créditos", "quantidade": 50, "creditos_entregues": 50, "preco_reais": calcular_preco_reais(50)},
        {"id": "100", "nome": "100 créditos", "quantidade": 100, "creditos_entregues": 100, "preco_reais": calcular_preco_reais(100)},
        {"id": "300", "nome": "300 créditos", "quantidade": 300, "creditos_entregues": 300, "preco_reais": calcular_preco_reais(300)},
        {"id": "400", "nome": "400 créditos (+20%)", "quantidade": 400, "creditos_entregues": calcular_creditos_entregues(400), "preco_reais": calcular_preco_reais(400), "destaque": True},
        {"id": "500", "nome": "500 créditos (+20%)", "quantidade": 500, "creditos_entregues": calcular_creditos_entregues(500), "preco_reais": calcular_preco_reais(500)},
        {"id": "1000", "nome": "1000 créditos (+20%)", "quantidade": 1000, "creditos_entregues": calcular_creditos_entregues(1000), "preco_reais": calcular_preco_reais(1000)},
    ]
    return {
        "pacotes": sugestoes,
        "regra": {
            "preco_por_credito_reais": PRECO_CREDITO,
            "bonus_acima_de": BONUS_THRESHOLD,
            "bonus_percentual": int(BONUS_PERCENT * 100),
        },
    }


@api_router.get("/creditos")
def creditos(user = Depends(require_api_key)):
    try:
        # Verificar se user tem as chaves necess?rias
        if "creditos" not in user or "creditos_usados" not in user:
            logging.error(f"Usu?rio sem chaves de cr?ditos: {user.keys()}")
            raise HTTPException(status_code=500, detail="Dados do usu?rio incompletos")
        
        disponiveis = creditos_disponiveis(user)
        
        return {
            "creditos": user.get("creditos", 0),
            "creditos_usados": user.get("creditos_usados", 0),
            "creditos_disponiveis": disponiveis,
            "usuario": {"id": user.get("id"), "nome": user.get("nome"), "email": user.get("email")}
        }
    except HTTPException:
        raise
    except KeyError as e:
        logging.error(f"Erro de chave em creditos: {e}, user keys: {list(user.keys()) if user else 'None'}")
        raise HTTPException(status_code=500, detail=f"Chave faltando: {str(e)}")
    except Exception as e:
        logging.error(f"Erro em creditos: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cr?ditos: {str(e)}")


@api_router.get("/perfil")
@limiter.limit("30 per minute")
def get_perfil(request: Request, user=Depends(require_api_key)):
    """Retorna dados do perfil do usu?rio (para edi??o em Atualizar cadastro)."""
    return {
        "id": user.get("id"),
        "nome": user.get("nome") or "",
        "email": user.get("email") or "",
        "cpf": user.get("cpf") or "",
        "telefone": user.get("telefone") or "",
    }


@api_router.patch("/perfil")
@limiter.limit("20 per minute")
def atualizar_perfil(request: Request, data: AtualizarPerfilInput, user=Depends(require_api_key)):
    """Atualiza nome, email, cpf e/ou telefone do usu?rio. CPF e telefone s?o necess?rios para comprar cr?ditos."""
    updates = []
    params = []
    if data.nome is not None:
        updates.append("nome = %s")
        params.append(data.nome.strip())
    if data.email is not None:
        updates.append("email = %s")
        params.append(data.email.strip())
    if data.cpf is not None:
        updates.append("cpf = %s")
        params.append(data.cpf.strip() or None)
    if data.telefone is not None:
        updates.append("telefone = %s")
        params.append(data.telefone.strip() or None)
    if not updates:
        return {"ok": True, "mensagem": "Nenhum campo alterado"}
    params.append(user["id"])
    sql = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
    db_execute(sql, tuple(params))
    row = db_select_one("SELECT id, nome, email, cpf, telefone FROM usuarios WHERE id = %s", (user["id"],))
    return {
        "ok": True,
        "mensagem": "Cadastro atualizado",
        "usuario": dict(row) if row else {},
    }


@api_router.get("/jobs")
@limiter.limit("30 per minute")
def listar_jobs(request: Request, user = Depends(require_api_key)):
    """Lista todos os jobs do usu?rio."""
    try:
        jobs = db_select(
            "SELECT id, modulo, status, created_at FROM research_jobs WHERE usuario_id = %s ORDER BY id DESC",
            (user["id"],)
        )

        # Formatar resposta conforme especificado
        response = [
            {
                "id": job["id"],
                "modulo": job.get("modulo", ""),
                "status": job["status"],
                "created_at": job.get("created_at").isoformat() if job.get("created_at") else None,
            }
            for job in jobs
        ]

        return response
    except Exception as e:
        logging.error(f"Erro em listar_jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@api_router.get("/job/{job_id}")
@api_router.get("/status/{job_id}")
@limiter.limit("30 per minute")  # Rate limit mais permissivo para polling
def status_job(request: Request, job_id: int, user = Depends(require_api_key)):
    """Verifica o status de um job de processamento ass?ncrono."""
    try:
        job = db_select_one(
            "SELECT * FROM research_jobs WHERE id = %s AND usuario_id = %s",
            (job_id, user["id"])
        )

        if not job:
            raise HTTPException(status_code=404, detail="Job n?o encontrado")

        response = {
            "request_id": job["id"],
            "project_id": job.get("project_id"),
            "status": job["status"],
            "modulo": job.get("modulo", ""),
            "created_at": job.get("created_at", "").isoformat() if job.get("created_at") else None
        }

        # Se o job estiver completo, incluir o resultado
        if job["status"] == "done" and job.get("resultado"):
            response["resultado"] = job["resultado"]
            
            # Se for metan?lise e tiver dados_extras com artigos, incluir artigos na resposta
            if job.get("dados_extras"):
                try:
                    dados_extras = json.loads(job["dados_extras"]) if isinstance(job["dados_extras"], str) else job["dados_extras"]
                    if isinstance(dados_extras, dict) and "artigos" in dados_extras:
                        response["artigos"] = dados_extras["artigos"]
                        response["total_artigos"] = dados_extras.get("total_artigos", len(dados_extras.get("artigos", [])))
                except:
                    pass  # Se n?o conseguir parsear, ignora

        # Se o job falhou, incluir o erro
        if job["status"] == "failed" and job.get("erro"):
            response["erro"] = job["erro"]
            response["detalhes"] = job["erro"]

        return response
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro em status_job: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

# ============================================
# ? ROTAS DE IA
# ============================================

@api_router.post("/critica")
@api_router.post("/critical_analysis")
@limiter.limit("10 per minute")
def rota_critica(request: Request, data: InputCritica, user = Depends(require_api_key)):
    try:
        foco_analise = data.foco_analise or "geral"
        custo = consumir_creditos(user["id"], "critica")

        # Criar job ass?ncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras, started_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (user["id"], "critica", "processing", data.texto_artigo, custo, json.dumps({"foco_analise": foco_analise}))
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_critica,
            args=(job_id, data.texto_artigo, foco_analise),
            daemon=True
        ).start()

        return JSONResponse(
            content={
                "request_id": job_id,
                "status": "processing"
            },
            status_code=202
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /critica")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@api_router.post("/meta_analysis/upload_articles")
@limiter.limit("5 per minute")
async def rota_upload_artigos_metanalise(
    request: Request, 
    files: list[UploadFile] = File(..., description="Lista de arquivos PDF/DOCX (m?x. 25)"),
    user = Depends(require_api_key)
):
    """
    Endpoint para upload m?ltiplo de artigos cient?ficos para metan?lise.
    Aceita at? 25 arquivos PDF/DOCX e faz an?lise PRISMA de cada um.
    """
    try:
        project_id = int(time.time())

        # Validar n?mero de arquivos
        if len(files) > 25:
            raise HTTPException(
                status_code=400, 
                detail="M?ximo de 25 artigos permitidos"
            )
        
        if len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um arquivo deve ser enviado"
            )
        
        # Validar formatos
        for file in files:
            if not file.filename or not file.filename.lower().endswith((".pdf", ".docx")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato inv?lido: {file.filename}. Apenas PDF e DOCX s?o suportados."
                )
        
        # Cobrar cr?ditos (custo por arquivo + an?lise PRISMA por artigo)
        custo_por_arquivo = 5  # pdf
        custo_analise_prisma = 15  # meta_etapa por artigo
        custo_total = (custo_por_arquivo + custo_analise_prisma) * len(files)
        consumir_creditos_total(user["id"], custo_total, "meta_analise_upload")
        
        # Importar m?dulos necess?rios (compat?vel com uvicorn api:app a partir de /app/backend)
        # read_docx j? est? definido neste m?dulo (api.py)
        try:
            from prisma_analyzer import analisar_artigo_prisma, gerar_resumo_analises
            from pdf_processor import extrair_texto_pdf
        except ImportError:
            try:
                from .prisma_analyzer import analisar_artigo_prisma, gerar_resumo_analises
                from .pdf_processor import extrair_texto_pdf
            except ImportError:
                import backend.prisma_analyzer as prisma_analyzer
                import backend.pdf_processor as pdf_processor
                analisar_artigo_prisma = prisma_analyzer.analisar_artigo_prisma
                gerar_resumo_analises = prisma_analyzer.gerar_resumo_analises
                extrair_texto_pdf = pdf_processor.extrair_texto_pdf
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        artigos_processados = []
        analises_prisma = []
        
        # Processar cada arquivo
        for idx, file in enumerate(files):
            try:
                extensao = file.filename.lower().split('.')[-1]
                temp_path = os.path.join(temp_dir, f"_temp_{secrets.token_hex(6)}_{idx}.{extensao}")
                
                # Salvar arquivo tempor?rio
                with open(temp_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                try:
                    # Extrair texto
                    if extensao == 'pdf':
                        texto_extraido = extrair_texto_pdf(temp_path)
                    elif extensao == 'docx':
                        texto_extraido = read_docx(temp_path)
                    else:
                        continue
                    
                    if isinstance(texto_extraido, list):
                        texto_extraido = "\n\n".join(texto_extraido)
                    
                    # Extrair t?tulo (primeiras linhas ou usar nome do arquivo)
                    titulo = file.filename.replace('.pdf', '').replace('.docx', '')
                    if texto_extraido:
                        linhas = texto_extraido.split('\n')[:5]
                        titulo_candidato = ' '.join([l.strip() for l in linhas if l.strip()][:2])
                        if len(titulo_candidato) > 10:
                            titulo = titulo_candidato[:200]
                    
                    # Analisar com PRISMA
                    analise = analisar_artigo_prisma(texto_extraido[:10000], titulo)
                    
                    artigos_processados.append({
                        "arquivo": file.filename,
                        "titulo": titulo,
                        "texto_extraido": texto_extraido[:1000],  # Primeiros 1000 chars para preview
                        "analise_prisma": analise
                    })
                    
                    analises_prisma.append(analise)
                    
                finally:
                    # Limpar arquivo tempor?rio
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                logging.error(f"Erro ao processar arquivo {file.filename}: {str(e)}")
                artigos_processados.append({
                    "arquivo": file.filename,
                    "erro": str(e),
                    "analise_prisma": None
                })
        
        # Gerar resumo consolidado
        resumo = gerar_resumo_analises(analises_prisma)
        
        # Registrar log
        registrar_log(
            user["id"],
            "meta_analise_upload",
            f"Upload de {len(files)} artigos",
            f"Processados {len(artigos_processados)} artigos",
            custo_total,
            request
        )
        
        return {
            "resultado": "Artigos processados e analisados com sucesso",
            "project_id": project_id,
            "total_artigos": len(artigos_processados),
            "artigos": artigos_processados,
            "resumo_analises": resumo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logging.error(f"Erro em upload_artigos_metanalise: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@api_router.post("/meta_analysis")
@api_router.post("/meta_analise")  # Alias para compatibilidade
@limiter.limit("10 per minute")
def rota_meta_analise(request: Request, data: InputMetaAnalise, user = Depends(require_api_key)):
    try:
        custo = consumir_creditos(user["id"], "meta_analise")

        # Preparar dados extras para o processamento
        dados_extras = {}
        if data.json_extracao:
            try:
                dados_extras["json_extracao"] = json.loads(data.json_extracao) if isinstance(data.json_extracao, str) else data.json_extracao
            except:
                dados_extras["json_extracao"] = data.json_extracao
        if data.estilo:
            dados_extras["estilo"] = data.estilo
        if data.manuscrito:
            dados_extras["manuscrito"] = data.manuscrito
        
        # Novo fluxo: incluir artigos analisados se fornecido
        if data.artigos_analisados:
            try:
                artigos = json.loads(data.artigos_analisados) if isinstance(data.artigos_analisados, str) else data.artigos_analisados
                dados_extras["artigos_analisados"] = artigos
            except:
                dados_extras["artigos_analisados"] = data.artigos_analisados
        project_id = data.project_id if data.project_id is not None else int(time.time())
        dados_extras["project_id"] = project_id
        dados_extras["usuario_id"] = user["id"]  # para Evidence Graph no job em background

        # Criar job ass?ncrono (project_id agrupa jobs para Evidence Graph)
        dados_extras_json = json.dumps(dados_extras) if dados_extras else None
        entrada_texto = data.texto_artigo if data.texto_artigo else (data.tema if data.tema else "Metan?lise")
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras, project_id, started_at) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
            (user["id"], "meta_analise", "processing", entrada_texto, custo, dados_extras_json, project_id)
        )

        # Iniciar processamento em background
        # Tema pode ser vazio no novo fluxo (usa artigos analisados)
        tema_processamento = data.tema if data.tema else ""
        threading.Thread(
            target=processar_job_meta_analise,
            args=(job_id, tema_processamento, data.etapa, data.texto_artigo, dados_extras),
            daemon=True
        ).start()

        return JSONResponse(
            content={
                "request_id": job_id,
                "project_id": project_id,
                "status": "processing",
                "etapa": data.etapa
            },
            status_code=202
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /meta_analise")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@api_router.post("/meta_analysis/escrever_artigo")
@limiter.limit("6 per minute")
def escrever_artigo_metanalise(request: Request, dados: EscreverArtigoRequest, user=Depends(require_api_key)):
    """
    Etapa 5: escrita de seção/artigo completo com base no project_id da metanálise.
    """
    try:
        secao = (dados.secao or "completo").strip().lower()
        custo = 15 if secao == "completo" else 5

        disponivel = creditos_disponiveis(user)
        if disponivel < custo:
            raise HTTPException(
                status_code=402,
                detail=f"Créditos insuficientes. Necessário: {custo}, disponível: {disponivel}",
            )

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id FROM research_jobs
                    WHERE project_id = %s AND usuario_id = %s
                    LIMIT 1
                    """,
                    (dados.project_id, user["id"]),
                )
                projeto = cursor.fetchone()
                if not projeto:
                    raise HTTPException(status_code=404, detail="Projeto não encontrado para este usuário.")
        finally:
            conn.close()

        entrada = json.dumps(
            {
                "project_id": dados.project_id,
                "tema": dados.tema,
                "secao": secao,
                "estilo_referencia": dados.estilo_referencia,
                "idioma": dados.idioma,
                "instrucoes_adicionais": dados.instrucoes_adicionais,
            },
            ensure_ascii=False,
        )

        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, project_id, started_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (user["id"], "escrever_artigo", "processing", entrada, custo, dados.project_id),
        )

        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes para executar esta ação.")

        def _processar_escrita():
            conn_local = get_connection()
            try:
                secoes = ["resumo", "introducao", "metodos", "resultados", "discussao"] if secao == "completo" else [secao]
                partes = []
                for s in secoes:
                    texto = escrever_secao_artigo(
                        project_id=dados.project_id,
                        tema=dados.tema,
                        secao=s,
                        estilo_referencia=dados.estilo_referencia,
                        idioma=dados.idioma,
                        instrucoes_adicionais=dados.instrucoes_adicionais,
                    )
                    partes.append(f"## {s.upper()}\n\n{texto}")

                resultado = "\n\n---\n\n".join(partes)
                with conn_local.cursor() as cursor:
                    cursor.execute(
                        "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                        ("done", resultado, job_id),
                    )
                conn_local.commit()
            except Exception as e:
                with conn_local.cursor() as cursor:
                    cursor.execute(
                        "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                        ("failed", str(e), job_id),
                    )
                conn_local.commit()
            finally:
                conn_local.close()

        threading.Thread(target=_processar_escrita, daemon=True).start()

        return JSONResponse(
            content={
                "request_id": job_id,
                "project_id": dados.project_id,
                "status": "processing",
                "custo": custo,
            },
            status_code=202,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@api_router.post("/pdf")
@limiter.limit("10 per minute")
async def rota_pdf(request: Request, file: UploadFile = File(...), user = Depends(require_api_key)):
    try:
        if not file.filename or not file.filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(status_code=400, detail="Formato inv?lido. Apenas PDF e DOCX s?o suportados.")

        # Cobrar cr?ditos antes de processar
        custo = consumir_creditos(user["id"], "pdf")

        extensao = file.filename.lower().split('.')[-1]
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"_temp_{secrets.token_hex(6)}.{extensao}")
        
        # Salvar arquivo
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            if extensao == 'pdf':
                texto_extraido = extrair_texto_pdf(temp_path)
            elif extensao == 'docx':
                texto_extraido = read_docx(temp_path)
            else:
                raise HTTPException(status_code=400, detail="Formato n?o suportado")
            
            if isinstance(texto_extraido, list):
                texto_extraido = "\n\n".join(texto_extraido)

            texto_log = texto_extraido[:500] if isinstance(texto_extraido, str) else str(texto_extraido)[:500]
            registrar_log(user["id"], "pdf", "[ARQUIVO]", texto_log, custo, request)

            return {"resultado": texto_extraido}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha ao processar arquivo: {str(e)}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


class TraducaoInput(BaseModel):
    """Texto a ser traduzido para portugu?s (usado pelo bot?o Traduzir texto)."""
    texto: str


@api_router.post("/traducao")
@limiter.limit("20 per minute")
def rota_traducao(request: Request, data: TraducaoInput, user=Depends(require_api_key)):
    """
    Traduz o texto extra?do para portugu?s brasileiro (Qwen/Groq quando dispon?vel).
    Usado quando o usu?rio clica em "Traduzir texto" na aba do texto extra?do.
    """
    if not data.texto or not data.texto.strip():
        raise HTTPException(status_code=400, detail="Texto n?o pode estar vazio")
    try:
        resultado_pt = obter_versao_portugues(data.texto.strip())
        return {"resultado_pt": resultado_pt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao traduzir: {str(e)}")


@api_router.post("/chat-followup")
@limiter.limit("20 per minute")
def rota_chat_followup(request: Request, data: ChatFollowUpInput, user = Depends(require_api_key)):
    """
    Processa mensagens de follow-up do chat, permitindo intera??o com respostas da IA.
    """
    try:
        if not data.mensagem or not data.mensagem.strip():
            raise HTTPException(status_code=400, detail="Mensagem n?o pode estar vazia")

        custo = consumir_creditos(user["id"], "chat_followup")

        # Construir contexto do hist?rico
        contexto_historico = ""
        if data.historico:
            for msg in data.historico[-5:]:  # ?ltimas 5 mensagens para contexto
                role = "Usu?rio" if msg.get("role") == "user" else "Assistente"
                contexto_historico += f"{role}: {msg.get('content', '')}\n\n"

        # Construir prompt contextualizado baseado no tipo de an?lise
        tipo_analise_nomes = {
            "critica": "An?lise Cr?tica",
            "critical_analysis": "An?lise Cr?tica",
            "meta_analise": "Metan?lise",
            "meta_analysis": "Metan?lise",
            "meta-analise": "Metan?lise",
        }
        
        nome_analise = tipo_analise_nomes.get(data.tipo_analise, data.tipo_analise)

        prompt = f"""Voc? ? um assistente especializado em an?lise cient?fica. O usu?rio est? interagindo com uma an?lise do tipo: {nome_analise}.

Contexto da an?lise anterior:
{contexto_historico if contexto_historico else "Esta ? a primeira intera??o ap?s a an?lise inicial."}

Texto do artigo (refer?ncia):
{data.texto_artigo[:2000] if data.texto_artigo else "N?o dispon?vel"}

Mensagem do usu?rio:
{data.mensagem}

Responda de forma clara, objetiva e ?til. Se o usu?rio pedir melhorias, sugest?es ou esclarecimentos, forne?a respostas pr?ticas e acion?veis. Mantenha o foco no contexto cient?fico e na an?lise realizada."""

        # Gerar resposta usando gpt_engine
        try:
            from .gpt_engine import gerar_resposta
        except ImportError:
            try:
                import gpt_engine
                gerar_resposta = gpt_engine.gerar_resposta
            except ImportError:
                import backend.gpt_engine as gpt_engine
                gerar_resposta = gpt_engine.gerar_resposta

        resposta = gerar_resposta(prompt, temperatura=0.7)  # Usa padr?o configurado (1000 tokens)

        # Registrar log
        registrar_log(
            user["id"],
            f"chat_{data.tipo_analise}",
            data.mensagem[:500],
            resposta[:500] if resposta else "",
            custo,
            request
        )

        return {
            "resultado": resposta,
            "resposta": resposta,  # Alias para compatibilidade
            "creditos_gastos": custo
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Erro em chat-followup: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar mensagem: {str(e)}")

# ============================================
# ? INCLUIR ROUTERS NA APLICA??O
# ============================================

app.include_router(api_router)

# Webhook Asaas (POST /genapi/webhook/asaas)
try:
    from backend.routes.asaas_webhook import router as asaas_webhook_router
except ImportError:
    try:
        from routes.asaas_webhook import router as asaas_webhook_router
    except ImportError:
        from .routes.asaas_webhook import router as asaas_webhook_router
app.include_router(asaas_webhook_router)

# Checkout cr?ditos (POST /genapi/checkout/creditos)
try:
    from backend.routes.checkout_creditos import router as checkout_router
except ImportError:
    try:
        from routes.checkout_creditos import router as checkout_router
    except ImportError:
        from .routes.checkout_creditos import router as checkout_router
app.include_router(checkout_router)

# Meta-analysis v2 (pipeline estruturado)
try:
    from backend.routers.meta import router as meta_v2_router
except ImportError:
    try:
        from routers.meta import router as meta_v2_router
    except ImportError:
        from .routers.meta import router as meta_v2_router
app.include_router(meta_v2_router)

# Log para debug: verificar se os routers foram inclu?dos
logging.warning(f"[DEBUG] Router inclu?do com prefixo: /genapi")
logging.warning(f"[DEBUG] Total de rotas ap?s incluir routers: {len(app.routes)}")

# ============================================
# ? EXECU??O LOCAL (para desenvolvimento)
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

