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

from flask import Flask, request, jsonify, g, Blueprint, Blueprint
from flask_cors import CORS  # ✅ Usar Flask-CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
# ✅ APLICAÇÃO FLASK
# ============================================

app = Flask(__name__)

# ✅ Criar Blueprint para todas as rotas da API (sem prefixo)
api_bp = Blueprint('api', __name__)

# ✅ CONFIGURAR CORS (RESTRITIVO E SEGURO)
# Configurar CORS apenas para o domínio do Vercel
CORS(app, 
     resources={
         r"/*": {
             "origins": ["https://medquestresearch.vercel.app"]
         }
     },
     supports_credentials=False,
     allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
     max_age=3600)

# ✅ Configuração de rate limiting
# Função para ignorar OPTIONS no rate limiting (evita erro 500 no preflight)
def key_func():
    if request.method == "OPTIONS":
        return None  # Não aplicar rate limit em OPTIONS
    return get_remote_address()

limiter = Limiter(
    key_func=key_func,
    app=app,
    default_limits=["100 per day", "10 per minute"],
    storage_uri="memory://",
)

# ============================================
# ✅ FUNÇÕES AUXILIARES
# ============================================

def gerar_token():
    return secrets.token_hex(32)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
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
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def registrar_log(usuario_id, modulo, entrada, saida, creditos):
    ip = request.remote_addr
    db_execute("""
        INSERT INTO gen_logs_uso (usuario_id, modulo, entrada, saida, creditos_gastos, ip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, modulo, entrada, saida, creditos, ip))

def read_docx(file_path):
    """Lê o conteúdo de um arquivo DOCX e retorna como string."""
    doc = Document(file_path)
    text = '\n'.join([p.text for p in doc.paragraphs])
    return text

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

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
    evitando timeout no PythonAnywhere.
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

@app.errorhandler(Exception)
def handle_error(e):
    """Handler global para capturar erros e retornar JSON."""
    import traceback
    
    # Log do erro
    print(f"❌ Erro capturado: {str(e)}")
    print(traceback.format_exc())
    
    # Determinar status code
    status_code = 500
    if hasattr(e, 'code'):
        status_code = e.code
    elif hasattr(e, 'status_code'):
        status_code = e.status_code
    
    # Retornar resposta JSON
    response = jsonify({
        "erro": "Erro interno do servidor",
        "detalhes": str(e) if app.debug else "Erro ao processar requisição"
    })
    response.status_code = status_code
    
    return response

# ============================================
# ✅ ROTAS BÁSICAS
# ============================================

@limiter.exempt
@app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({"status": "Medquestresearch API está ativa ✅", "version": "2.0"})

@limiter.exempt
@app.route("/ping")
def ping():
    return jsonify({"message": "pong", "timestamp": datetime.datetime.now().isoformat()})

@limiter.exempt
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

# ============================================
# ✅ ROTAS DE USUÁRIO
# ============================================

@api_bp.route("/cadastro", methods=["POST", "OPTIONS"])
def cadastro():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        nome = data.get("nome")
        email = data.get("email")
        senha = data.get("senha")

        if not nome or not email or not senha:
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400

        if db_select_one("SELECT * FROM usuarios WHERE email=%s", (email,)):
            return jsonify({"erro": "Email já cadastrado"}), 400

        senha_hash = hash_senha(senha)
        token = gerar_token()

        db_execute("""
            INSERT INTO usuarios (nome, email, senha_hash, creditos)
            VALUES (%s, %s, %s, 10)
        """, (nome, email, senha_hash))

        db_execute("UPDATE usuarios SET token=%s WHERE email=%s", (token, email))

        return jsonify({"status": "Usuário criado", "token": token})
    
    except Exception as e:
        return jsonify({"erro": "Erro ao criar usuário", "detalhes": str(e)}), 500

# ✅ ROTA LOGIN - ACEITA POST E OPTIONS
@api_bp.route("/login", methods=["POST", "OPTIONS"])
@limiter.exempt  # Exempt para garantir que OPTIONS não passe pelo rate limiter
def login():
    # Tratar OPTIONS primeiro (antes de qualquer processamento)
    # Flask-CORS deve adicionar os headers automaticamente
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    # Aplicar rate limit apenas para POST (key_func já ignora OPTIONS)
    # Mas vamos garantir que não haja erro
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados inválidos"}), 400
        
        email = data.get("email")
        senha = data.get("senha")

        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        row = db_select_one("SELECT * FROM usuarios WHERE email=%s", (email,))
        if not row:
            return jsonify({"erro": "Email não encontrado"}), 404

        if row["senha_hash"] != hash_senha(senha):
            return jsonify({"erro": "Senha incorreta"}), 401

        token = gerar_token()
        db_execute("UPDATE usuarios SET token=%s WHERE id=%s", (token, row["id"]))

        return jsonify({"token": token, "status": "Login realizado com sucesso"})
    
    except Exception as e:
        return jsonify({"erro": "Erro ao fazer login", "detalhes": str(e)}), 500

@api_bp.route("/creditos", methods=["GET", "OPTIONS"])
def creditos():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        # Verificar se user tem as chaves necessárias
        if "creditos" not in user or "creditos_usados" not in user:
            logging.error(f"Usuário sem chaves de créditos: {user.keys()}")
            return jsonify({"erro": "Erro ao buscar créditos", "detalhes": "Dados do usuário incompletos"}), 500

        disponiveis = creditos_disponiveis(user)
        
        return jsonify({
            "creditos": user.get("creditos", 0),
            "creditos_usados": user.get("creditos_usados", 0),
            "creditos_disponiveis": disponiveis
        })
    except KeyError as e:
        logging.error(f"Erro de chave em creditos: {e}, user keys: {list(user.keys()) if user else 'None'}")
        return jsonify({"erro": "Erro ao buscar créditos", "detalhes": f"Chave faltando: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Erro em creditos: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"erro": "Erro ao buscar créditos", "detalhes": str(e)}), 500

@api_bp.route("/jobs", methods=["GET", "OPTIONS"])
@limiter.limit("30 per minute")
def listar_jobs():
    """Lista todos os jobs do usuário."""
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

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

        return jsonify(response)
    except Exception as e:
        logging.error(f"Erro em listar_jobs: {e}")
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/job/<int:job_id>", methods=["GET", "OPTIONS"])
@api_bp.route("/status/<int:job_id>", methods=["GET", "OPTIONS"])
@limiter.limit("30 per minute")  # Rate limit mais permissivo para polling
def status_job(job_id):
    """Verifica o status de um job de processamento assíncrono."""
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        job = db_select_one(
            "SELECT * FROM research_jobs WHERE id = %s AND usuario_id = %s",
            (job_id, user["id"])
        )

        if not job:
            return jsonify({"erro": "Job não encontrado"}), 404

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

        return jsonify(response)
    except Exception as e:
        logging.error(f"Erro em status_job: {e}")
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

# ============================================
# ✅ ROTAS DE IA
# ============================================

@api_bp.route("/explicar", methods=["POST", "OPTIONS"])
@api_bp.route("/explain_concept", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_explicar():
    log_t("INICIO REQUEST")
    print(">>> ENTROU NA ROTA /explicar")
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputTexto(**request.json)
            texto_artigo = data.texto_artigo
            trecho = data.trecho
            nivel = data.nivel
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        if not trecho:
            return jsonify({"erro": "Campo 'trecho' é obrigatório"}), 400

        custo = 5
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        dados_extras = json.dumps({"trecho": trecho, "nivel": nivel})
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras) VALUES (%s, %s, %s, %s, %s, %s)",
            (user["id"], "explicar", "processing", texto_artigo, custo, dados_extras)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_explicar,
            args=(job_id, texto_artigo, trecho, nivel),
            daemon=True
        ).start()

        log_t("FIM REQUEST")
        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /explicar")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/critica", methods=["POST", "OPTIONS"])
@api_bp.route("/critical_analysis", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_critica():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputCritica(**request.json)
            texto_artigo = data.texto_artigo
            foco_analise = data.foco_analise or "geral"
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        custo = 7
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras) VALUES (%s, %s, %s, %s, %s, %s)",
            (user["id"], "critica", "processing", texto_artigo, custo, json.dumps({"foco_analise": foco_analise}))
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_critica,
            args=(job_id, texto_artigo, foco_analise),
            daemon=True
        ).start()

        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /critica")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/fatos", methods=["POST", "OPTIONS"])
@api_bp.route("/fact_checker", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_fatos():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputFatos(**request.json)
            texto_artigo = data.texto_artigo
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        custo = 5
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "fatos", "processing", texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_fatos,
            args=(job_id, texto_artigo),
            daemon=True
        ).start()

        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /fatos")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/perspectiva", methods=["POST", "OPTIONS"])
@api_bp.route("/perspective_research", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_perspectiva():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputPerspectiva(**request.json)
            texto_artigo = data.texto_artigo
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        custo = 10
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "perspectiva", "processing", texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_perspectiva,
            args=(job_id, texto_artigo),
            daemon=True
        ).start()

        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /perspectiva")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/mapa", methods=["POST", "OPTIONS"])
@api_bp.route("/structure_visualizer", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_mapa():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputMapa(**request.json)
            texto_artigo = data.texto_artigo
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        custo = 8
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "mapa", "processing", texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_mapa,
            args=(job_id, texto_artigo),
            daemon=True
        ).start()

        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /mapa")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/structure_mapper", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_structure_mapper():
    try:
        user = autenticar(request)
        if not user:
            return jsonify({"erro": "Não autorizado"}), 401

        try:
            data = InputMapa(**request.json)
            texto_artigo = data.texto_artigo
        except Exception as e:
            return jsonify({"erro": "Dados inválidos", "detalhes": str(e)}), 400

        custo = 6
        if not debitar_creditos(user["id"], custo):
            return jsonify({"erro": "Créditos insuficientes"}), 402

        # Criar job assíncrono
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], "structure_mapper", "processing", texto_artigo, custo)
        )

        # Iniciar processamento em background
        threading.Thread(
            target=processar_job_structure_mapper,
            args=(job_id, texto_artigo),
            daemon=True
        ).start()

        return jsonify({
            "request_id": job_id,
            "status": "processing"
        }), 202
    except Exception as e:
        import traceback
        print("ERRO NA ROTA /structure_mapper")
        traceback.print_exc()
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@api_bp.route("/pdf", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def rota_pdf():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    if "file" not in request.files:
        return jsonify({"erro": "Arquivo não enviado", "detalhes": "Campo 'file' não encontrado"}), 400

    arquivo = request.files["file"]

    if arquivo.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado"}), 400

    if not arquivo.filename or not arquivo.filename.lower().endswith((".pdf", ".docx")):
        return jsonify({"erro": "Formato inválido", "detalhes": "Apenas PDF e DOCX"}), 400

    extensao = arquivo.filename.lower().split('.')[-1]
    
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"_temp_{secrets.token_hex(6)}.{extensao}")
    arquivo.save(temp_path)

    try:
        if extensao == 'pdf':
            texto_extraido = extrair_texto_pdf(temp_path)
        elif extensao == 'docx':
            texto_extraido = read_docx(temp_path)
        else:
            return jsonify({"erro": "Formato não suportado"}), 400
        
        if isinstance(texto_extraido, list):
            texto_extraido = "\n\n".join(texto_extraido)

        texto_log = texto_extraido[:500] if isinstance(texto_extraido, str) else str(texto_extraido)[:500]
        registrar_log(user["id"], "pdf", "[ARQUIVO]", texto_log, 0)

        return jsonify({"resultado": texto_extraido})

    except Exception as e:
        return jsonify({"erro": "Falha ao processar arquivo", "detalhes": str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ============================================
# ✅ REGISTRAR BLUEPRINT COM PREFIXO /genapi
# ============================================
app.register_blueprint(api_bp)

# ============================================
# ✅ EXECUÇÃO LOCAL (para desenvolvimento)
# ============================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

