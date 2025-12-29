# ============================================
# ✅ IMPORTS E CONFIGURAÇÕES INICIAIS
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
from functools import wraps

from fastapi import FastAPI, Request, HTTPException, Depends, Header, File, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, validator
from typing import Optional

# process_chunks e combine_responses agora são usados apenas dentro de run_with_two_chunks
from docx import Document  # pyright: ignore[reportMissingImports]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================
# ✅ AJUSTAR IMPORTAÇÕES PARA FUNCIONAR TANTO NA RAIZ QUANTO EM backend/
# ============================================

# Banco de dados - tentar relativo primeiro, depois absoluto
# Se estiver em backend/, adicionar o diretório ao path para importações absolutas funcionarem
_parent_dir = os.path.dirname(BASE_DIR)
if _parent_dir not in sys.path and os.path.basename(BASE_DIR) == "backend":
    sys.path.insert(0, _parent_dir)
    # Também adicionar backend/ ao path
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
        # Última tentativa: importar do backend
        import backend.database as database  # type: ignore[reportMissingImports]
        db_select = database.db_select
        db_select_one = database.db_select_one
        db_execute = database.db_execute
        get_connection = database.get_connection

try:
    from .explain_concept import explicar_conceito
except ImportError:
    try:
        import explain_concept
        explicar_conceito = explain_concept.explicar_conceito
    except ImportError:
        import backend.explain_concept as explain_concept  # type: ignore[reportMissingImports]
        explicar_conceito = explain_concept.explicar_conceito

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
    from .Fact_checker import verificar_fatos
except ImportError:
    try:
        import Fact_checker
        verificar_fatos = Fact_checker.verificar_fatos
    except ImportError:
        import backend.Fact_checker as Fact_checker  # type: ignore[reportMissingImports]
        verificar_fatos = Fact_checker.verificar_fatos

try:
    from .Perspective_research import buscar_perspectivas_pubmed
except ImportError:
    try:
        import Perspective_research
        buscar_perspectivas_pubmed = Perspective_research.buscar_perspectivas_pubmed
    except ImportError:
        import backend.Perspective_research as Perspective_research  # type: ignore[reportMissingImports]
        buscar_perspectivas_pubmed = Perspective_research.buscar_perspectivas_pubmed

try:
    from .structure_visualizer import visualizar_estrutura
except ImportError:
    try:
        import structure_visualizer
        visualizar_estrutura = structure_visualizer.visualizar_estrutura
    except ImportError:
        import backend.structure_visualizer as structure_visualizer  # type: ignore[reportMissingImports]
        visualizar_estrutura = structure_visualizer.visualizar_estrutura

try:
    from .structure_mapper import gerar_mapa_estrutura
except ImportError:
    try:
        import structure_mapper
        gerar_mapa_estrutura = structure_mapper.gerar_mapa_estrutura
    except ImportError:
        import backend.structure_mapper as structure_mapper  # type: ignore[reportMissingImports]
        gerar_mapa_estrutura = structure_mapper.gerar_mapa_estrutura

try:
    from .pdf_processor import extrair_texto_pdf
except ImportError:
    try:
        import pdf_processor
        extrair_texto_pdf = pdf_processor.extrair_texto_pdf
    except ImportError:
        import backend.pdf_processor as pdf_processor  # type: ignore[reportMissingImports]
        extrair_texto_pdf = pdf_processor.extrair_texto_pdf

# ============================================
# ✅ APLICAÇÃO FASTAPI
# ============================================

app = FastAPI(title="MedQuestResearch API", version="2.0")

# ✅ CONFIGURAR CORS (RESTRITIVO E SEGURO)
# Configurar CORS apenas para o domínio do Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://medquestresearch.vercel.app"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    max_age=3600,
)

# ✅ Configuração de rate limiting
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================
# ✅ MODELOS PYDANTIC
# ============================================

class CadastroRequest(BaseModel):
    nome: str
    email: str
    senha: str

class LoginRequest(BaseModel):
    email: str
    senha: str

class ExplicarRequest(BaseModel):
    texto_artigo: str
    trecho: str
    nivel: str

class CriticaRequest(BaseModel):
    texto_artigo: str
    pergunta: Optional[str] = None

class FatosRequest(BaseModel):
    texto_artigo: str
    afirmacoes: list

class PerspectivaRequest(BaseModel):
    texto_artigo: str
    pergunta: str

class MapaRequest(BaseModel):
    texto_artigo: str

# ============================================
# ✅ FUNÇÕES AUXILIARES
# ============================================

def gerar_token():
    return secrets.token_hex(32)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(authorization: Optional[str] = Header(None)):
    """Função de autenticação para FastAPI."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    row = db_select_one("SELECT * FROM usuarios WHERE token=%s", (token,))
    return row

def creditos_disponiveis(usuario):
    return max(0, usuario["creditos"] - usuario["creditos_usados"])

def debitar_creditos(usuario_id, qtd):
    """Debita créditos apenas se houver créditos disponíveis suficientes."""
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
        print(f"❌ ERRO ao debitar créditos: {e}")
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
    """Lê o conteúdo de um arquivo DOCX e retorna como string."""
    doc = Document(file_path)
    text = '\n'.join([p.text for p in doc.paragraphs])
    return text

async def require_api_key(authorization: str = Header(None)):
    """Dependency para autenticação em rotas FastAPI."""
    user = autenticar(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return user

def log_t(msg):
    """Função auxiliar para logging com timestamp."""
    logging.warning(f"[TIMER] {msg} @ {time.time():.2f}")

def run_with_two_chunks(
    texto: str,
    process_func,
    chunk_size: int = 1800,
    overlap: int = 300,
    max_chunks: int = 2
):
    """
    Executa processamento de IA em no máximo DOIS chunks,
    evitando timeout no servidor.
    """
    from .chunker import chunk_text, combine_responses

    log_t("ANTES chunking")
    chunks = chunk_text(texto, chunk_size=chunk_size, overlap=overlap)
    log_t("DEPOIS chunking")

    # Segurança absoluta: no máximo 2 chunks
    chunks = chunks[:max_chunks]

    respostas = []
    for i, chunk in enumerate(chunks, 1):
        log_t(f"ANTES OpenAI chunk {i}")
        resposta = process_func(chunk)
        log_t(f"DEPOIS OpenAI chunk {i}")
        respostas.append(resposta)

    log_t("ANTES montagem resposta")
    texto_final = combine_responses(respostas)
    log_t("DEPOIS montagem resposta")

    aviso = (
        "\n\n⚠️ Nota: esta análise foi gerada a partir de uma parte do texto "
        "para garantir rapidez e estabilidade da plataforma."
    )

    return texto_final + aviso

# ============================================
# ✅ FUNÇÕES DE PROCESSAMENTO ASSÍNCRONO
# ============================================

def processar_job_explicar(job_id: int, texto_artigo: str, trecho: str, nivel: str):
    """Processa job de explicação de conceito em background."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - explicar")
        
        # Limite defensivo
        texto_artigo = texto_artigo[:6000]
        
        def processar_chunk(chunk):
            return explicar_conceito(chunk, trecho, nivel)
        
        # Chamada pesada
        resultado = run_with_two_chunks(
            texto_artigo,
            processar_chunk,
            chunk_size=1800,
            overlap=300
        )
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - explicar")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - explicar\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)  # Limitar tamanho do erro
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def processar_job_critica(job_id: int, texto_artigo: str, foco_analise: str = "geral"):
    """Processa job de análise crítica em background - SEM chunking para análise focada."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - critica (foco: {foco_analise})")
        
        # Limitar texto drasticamente para análise focada (sem chunking)
        texto_artigo = texto_artigo[:3000]  # Reduzido de 4000 para 3000
        
        # Chamada direta SEM chunking - análise focada é mais rápida
        resultado = aplicar_leitura_critica(texto_artigo, foco_analise)
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - critica")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - critica\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def processar_job_fatos(job_id: int, texto_artigo: str):
    """Processa job de verificação de fatos em background - SEM chunking."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - fatos")
        
        # Limitar texto e chamar diretamente, sem chunking
        texto_artigo = texto_artigo[:4000]
        resultado = verificar_fatos(texto_artigo)
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - fatos")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - fatos\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def processar_job_perspectiva(job_id: int, texto_artigo: str):
    """Processa job de pesquisa de perspectivas em background."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - perspectiva")
        
        # Limitar texto para reduzir tempo de processamento
        texto_artigo = texto_artigo[:4000]
        
        def processar_chunk(chunk):
            return buscar_perspectivas_pubmed(chunk)
        
        resultado = run_with_two_chunks(
            texto_artigo,
            processar_chunk,
            chunk_size=2000,  # Aumentado para reduzir número de chunks
            overlap=200  # Reduzido para acelerar
        )
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - perspectiva")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - perspectiva\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def processar_job_mapa(job_id: int, texto_artigo: str):
    """Processa job de visualização de estrutura em background - SEM chunking."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - mapa")
        
        # Limitar texto e chamar diretamente, sem chunking
        texto_artigo = texto_artigo[:4000]
        resultado = visualizar_estrutura(texto_artigo)
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - mapa")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - mapa\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

def processar_job_structure_mapper(job_id: int, texto_artigo: str):
    """Processa job de mapeamento de estrutura em background - SEM chunking."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - structure_mapper")
        
        # Limitar texto e chamar diretamente, sem chunking
        texto_artigo = texto_artigo[:4000]
        resultado = gerar_mapa_estrutura(texto_artigo)
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s WHERE id=%s",
                    ("done", resultado, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - structure_mapper")
        
    except Exception:
        erro = traceback.format_exc()
        logging.error(f"[RESEARCH JOB {job_id}] erro - structure_mapper\n{erro}")
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        # autocommit=False para permitir controle explícito do commit
        conn = get_connection(autocommit=False)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, erro=%s WHERE id=%s",
                    ("failed", erro[:1000], job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()  # Commit explícito na mesma conexão
            logging.error(f"[RESEARCH JOB {job_id}] UPDATE erro - job_id={job_id}, linhas_afetadas={rowcount}")
        finally:
            conn.close()

# ============================================
# ✅ MODELOS PYDANTIC PARA VALIDAÇÃO
# ============================================

class InputTexto(BaseModel):
    texto_artigo: str
    trecho: Optional[str] = None
    nivel: Optional[str] = "graduação"

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo não pode estar vazio")
        return v

class InputCritica(BaseModel):
    texto_artigo: str
    foco_analise: Optional[str] = "geral"  # Método de análise crítica escolhido

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo não pode estar vazio")
        return v

class InputFatos(BaseModel):
    texto_artigo: str

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo não pode estar vazio")
        return v

class InputPerspectiva(BaseModel):
    texto_artigo: str

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo não pode estar vazio")
        return v

class InputMapa(BaseModel):
    texto_artigo: str

    @validator('texto_artigo')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError("texto_artigo não pode estar vazio")
        return v

# ============================================
# ✅ HANDLER DE ERROS GLOBAL
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"erro": str(exc)}
    )

# ============================================
# ✅ ROTAS BÁSICAS
# ============================================

@app.get("/")
def index():
    return {"status": "Medquestresearch API está ativa ✅", "version": "2.0"}

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

# ============================================
# ✅ ROTAS DE USUÁRIO
# ============================================

@app.post("/cadastro")
def cadastro(data: CadastroRequest):
    try:
        if db_select_one("SELECT * FROM usuarios WHERE email=%s", (data.email,)):
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        senha_hash = hash_senha(data.senha)
        token = gerar_token()

        db_execute("""
            INSERT INTO usuarios (nome, email, senha_hash, creditos)
            VALUES (%s, %s, %s, 10)
        """, (data.nome, data.email, senha_hash))

        db_execute("UPDATE usuarios SET token=%s WHERE email=%s", (token, data.email))

        return {"status": "Usuário criado", "token": token}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

@app.post("/login")
@limiter.limit("5 per minute")
def login(data: LoginRequest):
    try:
        row = db_select_one("SELECT * FROM usuarios WHERE email=%s", (data.email,))
        if not row:
            raise HTTPException(status_code=404, detail="Email não encontrado")

        if row["senha_hash"] != hash_senha(data.senha):
            raise HTTPException(status_code=401, detail="Senha incorreta")

        token = gerar_token()
        db_execute("UPDATE usuarios SET token=%s WHERE id=%s", (token, row["id"]))

        return {"token": token, "status": "Login realizado com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@app.get("/creditos")
def creditos(user = Depends(require_api_key)):
    try:
        # Verificar se user tem as chaves necessárias
        if "creditos" not in user or "creditos_usados" not in user:
            logging.error(f"Usuário sem chaves de créditos: {user.keys()}")
            raise HTTPException(status_code=500, detail="Dados do usuário incompletos")
        
        disponiveis = creditos_disponiveis(user)
        
        return {
            "creditos": user.get("creditos", 0),
            "creditos_usados": user.get("creditos_usados", 0),
            "creditos_disponiveis": disponiveis
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
        raise HTTPException(status_code=500, detail=f"Erro ao buscar créditos: {str(e)}")

@app.get("/jobs")
@limiter.limit("30 per minute")
def listar_jobs(user = Depends(require_api_key)):
    """Lista todos os jobs do usuário."""
    try:
        jobs = db_select(
            "SELECT id, modulo, status FROM research_jobs WHERE usuario_id = %s ORDER BY id DESC",
            (user["id"],)
        )

        # Formatar resposta conforme especificado
        response = [
            {
                "id": job["id"],
                "modulo": job.get("modulo", ""),
                "status": job["status"]
            }
            for job in jobs
        ]

        return response
    except Exception as e:
        logging.error(f"Erro em listar_jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/job/{job_id}")
@app.get("/status/{job_id}")
@limiter.limit("30 per minute")  # Rate limit mais permissivo para polling
def status_job(job_id: int, user = Depends(require_api_key)):
    """Verifica o status de um job de processamento assíncrono."""
    try:
        job = db_select_one(
            "SELECT * FROM research_jobs WHERE id = %s AND usuario_id = %s",
            (job_id, user["id"])
        )

        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")

        response = {
            "request_id": job["id"],
            "status": job["status"],
            "modulo": job.get("modulo", ""),
            "created_at": job.get("created_at", "").isoformat() if job.get("created_at") else None
        }

        # Se o job estiver completo, incluir o resultado
        if job["status"] == "done" and job.get("resultado"):
            response["resultado"] = job["resultado"]

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
# ✅ ROTAS DE IA
# ============================================

@app.post("/explicar")
@app.post("/explain_concept")
@limiter.limit("10 per minute")
def rota_explicar(data: InputTexto, request: Request, user = Depends(require_api_key)):
    log_t("INICIO REQUEST")
    print(">>> ENTROU NA ROTA /explicar")
    try:
        if not data.trecho:
            raise HTTPException(status_code=400, detail="Campo 'trecho' é obrigatório")

        custo = 5
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        dados_extras = json.dumps({"trecho": data.trecho, "nivel": data.nivel})
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras) VALUES (%s, %s, %s, %s, %s, %s)",
            (user["id"], "explicar", "processing", data.texto_artigo, custo, dados_extras)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_explicar,
            args=(job_id, data.texto_artigo, data.trecho, data.nivel),
            daemon=True
        ).start()

        log_t("FIM REQUEST")
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
        print("ERRO NA ROTA /explicar")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/critica")
@app.post("/critical_analysis")
@limiter.limit("10 per minute")
def rota_critica(data: InputCritica, user = Depends(require_api_key)):
    try:
        foco_analise = data.foco_analise or "geral"
        custo = 7
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras) VALUES (%s, %s, %s, %s, %s, %s)",
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

@app.post("/fatos")
@app.post("/fact_checker")
@limiter.limit("10 per minute")
def rota_fatos(data: InputFatos, user = Depends(require_api_key)):
    try:
        custo = 5
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "fatos", "processing", data.texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_fatos,
            args=(job_id, data.texto_artigo),
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
        print("ERRO NA ROTA /fatos")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/perspectiva")
@app.post("/perspective_research")
@limiter.limit("10 per minute")
def rota_perspectiva(data: InputPerspectiva, user = Depends(require_api_key)):
    try:
        custo = 10
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "perspectiva", "processing", data.texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_perspectiva,
            args=(job_id, data.texto_artigo),
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
        print("ERRO NA ROTA /perspectiva")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/mapa")
@app.post("/structure_visualizer")
@limiter.limit("10 per minute")
def rota_mapa(data: InputMapa, user = Depends(require_api_key)):
    try:
        custo = 8
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "mapa", "processing", data.texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_mapa,
            args=(job_id, data.texto_artigo),
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
        print("ERRO NA ROTA /mapa")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/structure_mapper")
@limiter.limit("10 per minute")
def rota_structure_mapper(data: InputMapa, user = Depends(require_api_key)):
    try:
        custo = 6
        if not debitar_creditos(user["id"], custo):
            raise HTTPException(status_code=402, detail="Créditos insuficientes")

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "structure_mapper", "processing", data.texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_structure_mapper,
            args=(job_id, data.texto_artigo),
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
        print("ERRO NA ROTA /structure_mapper")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/pdf")
@limiter.limit("10 per minute")
async def rota_pdf(file: UploadFile = File(...), user = Depends(require_api_key), request: Request = None):
    try:
        if not file.filename or not file.filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(status_code=400, detail="Formato inválido. Apenas PDF e DOCX são suportados.")

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
                raise HTTPException(status_code=400, detail="Formato não suportado")
            
            if isinstance(texto_extraido, list):
                texto_extraido = "\n\n".join(texto_extraido)

            texto_log = texto_extraido[:500] if isinstance(texto_extraido, str) else str(texto_extraido)[:500]
            registrar_log(user["id"], "pdf", "[ARQUIVO]", texto_log, 0, request)

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

# ============================================
# ✅ EXECUÇÃO LOCAL (para desenvolvimento)
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

