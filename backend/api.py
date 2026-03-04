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
import re
from functools import wraps
from psycopg2 import IntegrityError

# Carregar variáveis de ambiente do arquivo .env (local). Em produção/Railway as vars vêm do ambiente.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logging.info(f"[ENV] .env carregado de: {env_path}")
    else:
        load_dotenv()  # tenta diretório atual; em produção não existe .env e está ok
except ImportError:
    pass  # python-dotenv opcional em produção
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

# process_chunks e combine_responses agora são usados apenas dentro de run_with_two_chunks
from docx import Document  # pyright: ignore[reportMissingImports]

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
    from .meta_analysis import gerar_meta_analise
except ImportError:
    try:
        import meta_analysis
        gerar_meta_analise = meta_analysis.gerar_meta_analise
    except ImportError:
        import backend.meta_analysis as meta_analysis  # type: ignore[reportMissingImports]
        gerar_meta_analise = meta_analysis.gerar_meta_analise

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

# ============================================
# ✅ APLICAÇÃO FASTAPI
# ============================================

app = FastAPI(title="MedQuestResearch API", version="2.0")

# ✅ ROUTER COM PREFIXO /genapi PARA TODAS AS ROTAS DE API
api_router = APIRouter(prefix="/genapi")

# ✅ Configuração de rate limiting (adicionar primeiro)
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ✅ CONFIGURAÇÃO CORS CORRETA E SIMPLES (adicionar por último para executar primeiro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://medquestresearch.up.railway.app",
    ],
    allow_credentials=False,   # 🔥 IMPORTANTE: você usa token no header, não cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ✅ MODELOS PYDANTIC
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

def gerar_hash_senha(senha):
    return hash_senha(senha)

def gerar_hash_senha(senha):
    return hash_senha(senha)

def creditos_disponiveis(usuario):
    return max(0, usuario["creditos"] - usuario["creditos_usados"])

def adicionar_creditos_usuario(usuario_id, qtd):
    """Adiciona créditos a um usuário."""
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
        print(f"❌ ERRO ao adicionar créditos: {e}")
        return False
    finally:
        conn.close()

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

def get_current_user(authorization: str = Header(None)):
    """Autenticação: extrai token do header (Bearer ou puro) e busca usuário no banco."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Não autorizado")
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Não autorizado")
    row = db_select_one("SELECT * FROM usuarios WHERE token = %s", (token,))
    if not row:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return dict(row)

def require_api_key(authorization: str = Header(None)):
    """Dependency para autenticação em rotas FastAPI."""
    return get_current_user(authorization)


ADMIN_EMAIL = "prof.edesio@gmail.com"


def require_admin(authorization: str = Header(None)):
    """Dependency: apenas usuário admin (prof.edesio@gmail.com) pode acessar."""
    user = get_current_user(authorization)
    email = (user.get("email") or "").strip().lower()
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador.")
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
    try:
        from .chunker import chunk_text, combine_responses
    except ImportError:
        try:
            from chunker import chunk_text, combine_responses
        except ImportError:
            import backend.chunker as _chunker
            chunk_text = _chunker.chunk_text
            combine_responses = _chunker.combine_responses

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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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

def processar_job_meta_analise(job_id: int, tema: str, etapa: str = "1", texto_artigo: str = None, dados_extras: dict = None):
    """Processa job de metanálise em background."""
    try:
        logging.warning(f"[RESEARCH JOB {job_id}] início - meta_analise (etapa: {etapa}, tema: {tema})")
        
        # Limitar texto se fornecido
        if texto_artigo:
            texto_artigo = texto_artigo[:6000]
        
        # Chamar função de metanálise (agora retorna dict com 'resultado' e 'artigos')
        resultado_dict = gerar_meta_analise(tema=tema, etapa=etapa, texto_artigo=texto_artigo, dados_extras=dados_extras)
        
        resultado_texto = resultado_dict.get('resultado', '')
        artigos_encontrados = resultado_dict.get('artigos', [])
        total_artigos = resultado_dict.get('total_artigos', 0)
        
        # Preparar dados extras com artigos (se houver)
        dados_extras_atualizados = dados_extras.copy() if dados_extras else {}
        if artigos_encontrados:
            dados_extras_atualizados['artigos'] = artigos_encontrados
            dados_extras_atualizados['total_artigos'] = total_artigos
        
        # Usar conexão explícita com commit explícito para garantir funcionamento em threads
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Salvar resultado e dados extras (com artigos)
                dados_extras_json = json.dumps(dados_extras_atualizados) if dados_extras_atualizados else None
                cursor.execute(
                    "UPDATE research_jobs SET status=%s, resultado=%s, dados_extras=%s WHERE id=%s",
                    ("done", resultado_texto, dados_extras_json, job_id)
                )
                rowcount = cursor.rowcount
            conn.commit()
            logging.warning(f"[RESEARCH JOB {job_id}] UPDATE concluído - job_id={job_id}, linhas_afetadas={rowcount}, artigos={len(artigos_encontrados)}")
        finally:
            conn.close()
        
        logging.warning(f"[RESEARCH JOB {job_id}] concluído - meta_analise")
        
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

class InputMetaAnalise(BaseModel):
    tema: Optional[str] = ""  # Tema agora é opcional (novo fluxo usa upload de artigos)
    etapa: Optional[str] = "1"  # 1=PICO+Busca, 2=Extração, 3=Redação, 4=Verificação
    texto_artigo: Optional[str] = None  # Opcional - usado apenas nas etapas 2-4
    json_extracao: Optional[str] = None
    estilo: Optional[str] = "Vancouver"  # Vancouver ou ABNT
    manuscrito: Optional[str] = None
    artigos_analisados: Optional[str] = None  # JSON string com artigos analisados (novo fluxo)

# ============================================
# ✅ HANDLER DE ERROS GLOBAL
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções."""
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
            "erro": "Rota não encontrada",
            "path": str(request.url.path),
            "message": "Verifique se a rota está correta e se o servidor está rodando"
        }
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

@app.get("/cors-test")
def cors_test():
    """Rota de teste para verificar se CORS está funcionando"""
    return {
        "status": "CORS Test",
        "message": "Se você vê esta mensagem, CORS está funcionando!",
        "timestamp": datetime.datetime.now().isoformat()
    }

@api_router.get("/test-db")
def test_db():
    """Rota de teste para verificar se o banco de dados está acessível"""
    try:
        if not os.getenv("DATABASE_URL"):
            return {
                "ok": False,
                "erro": "DATABASE_URL não configurada",
                "dica": "Configure a variável DATABASE_URL no ambiente (Railway ou .env)"
            }
        
        r = db_select_one("SELECT count(*) AS total FROM usuarios")
        return {
            "ok": True,
            "usuarios": r["total"],
            "message": "Banco de dados está acessível!"
        }
    except Exception as e:
        return {
            "ok": False,
            "erro": str(e),
            "tipo": type(e).__name__
        }

# ============================================
# ✅ ROTAS DE ADMINISTRAÇÃO (CRÉDITOS)
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
    Lista todos os custos configurados para cada tipo de requisição.
    Requer autenticação de administrador.
    """
    try:
        custos = get_all_costs()
        return {
            "custos": custos,
            "total_modulos": len(custos),
            "observacao": "Valores podem ser ajustados via variáveis de ambiente CREDIT_COST_<MODULO>"
        }
    except Exception as e:
        logging.error(f"Erro ao listar custos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar custos: {str(e)}")


@api_router.get("/admin/metricas-creditos")
@limiter.limit("30 per minute")
def metricas_creditos(request: Request, user=Depends(require_admin)):
    """
    Dashboard de métricas de créditos: auditoria, uso por módulo, compras.
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

        # Uso por módulo (consumo)
        por_modulo = db_select(
            """
            SELECT modulo, COUNT(*) AS qtd_registros, COALESCE(SUM(custo_total), 0)::bigint AS total_creditos
            FROM historico_creditos
            WHERE tipo = 'consumo' AND modulo IS NOT NULL
            GROUP BY modulo
            ORDER BY total_creditos DESC
            """
        )

        # Últimos 50 registros (auditoria)
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
    Adiciona créditos a um usuário.
    Pode ser identificado por ID ou email.
    """
    try:
        # Buscar usuário por ID ou email
        if data.usuario_id:
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE id = %s", (data.usuario_id,))
        elif data.email:
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE email = %s", (data.email,))
        else:
            raise HTTPException(status_code=400, detail="Deve fornecer usuario_id ou email")

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Adicionar créditos usando função auxiliar
        if not adicionar_creditos_usuario(usuario["id"], data.quantidade):
            raise HTTPException(status_code=500, detail="Erro ao atualizar créditos no banco de dados")

        # Buscar dados atualizados
        usuario_atualizado = db_select_one(
            "SELECT id, nome, email, creditos, creditos_usados FROM usuarios WHERE id = %s",
            (usuario["id"],)
        )

        return {
            "mensagem": f"Créditos adicionados com sucesso",
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
        logging.error(f"Erro ao adicionar créditos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar créditos: {str(e)}")

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
# ✅ ROTAS DE USUÁRIO
# ============================================

@api_router.get("/test")
def test_router():
    """Rota de teste para verificar se o router está funcionando."""
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

        # Buscar usuário criado, gerar token e retornar (login automático pós-cadastro)
        row = db_select_one("SELECT id, nome, email, creditos, creditos_usados FROM usuarios WHERE email=%s", (data.email,))
        if not row:
            return JSONResponse(status_code=500, content={"erro": "Erro ao criar usuário"})

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
            "mensagem": "Usuário criado com sucesso"
        }

    except IntegrityError:
        return JSONResponse(
            status_code=400,
            content={"erro": "Email já cadastrado"}
        )

    except Exception as e:
        print("❌ ERRO NO CADASTRO:")
        print(traceback.format_exc())  # 🔥 ISSO MOSTRA O ERRO NO LOG

        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
        )

@api_router.post("/login")
@limiter.limit("5 per minute")
def login(request: Request, data: LoginRequest):
    try:
        # Verificar se o banco de dados está configurado
        if not os.getenv("DATABASE_URL"):
            logging.error("DATABASE_URL não configurada")
            raise HTTPException(
                status_code=503,
                detail="Banco de dados não configurado. Configure DATABASE_URL no ambiente."
            )
        
        row = db_select_one("SELECT * FROM usuarios WHERE email=%s", (data.email,))
        if not row:
            raise HTTPException(status_code=404, detail="Email não encontrado")

        if row["senha_hash"] != hash_senha(data.senha):
            raise HTTPException(status_code=401, detail="Senha incorreta")

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
# R$ 0,25/crédito; +20% de bônus acima de 300 créditos
# ============================================

PRECO_CREDITO = 0.25
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
    """Preço em R$ para comprar essa quantidade: valor = quantidade * PRECO_CREDITO."""
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
    Lista pacotes de créditos: R$ 0,25/crédito; +20% de bônus acima de 300 créditos.
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
        # Verificar se user tem as chaves necessárias
        if "creditos" not in user or "creditos_usados" not in user:
            logging.error(f"Usuário sem chaves de créditos: {user.keys()}")
            raise HTTPException(status_code=500, detail="Dados do usuário incompletos")
        
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
        raise HTTPException(status_code=500, detail=f"Erro ao buscar créditos: {str(e)}")


@api_router.get("/perfil")
@limiter.limit("30 per minute")
def get_perfil(request: Request, user=Depends(require_api_key)):
    """Retorna dados do perfil do usuário (para edição em Atualizar cadastro)."""
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
    """Atualiza nome, email, cpf e/ou telefone do usuário. CPF e telefone são necessários para comprar créditos."""
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

@api_router.get("/job/{job_id}")
@api_router.get("/status/{job_id}")
@limiter.limit("30 per minute")  # Rate limit mais permissivo para polling
def status_job(request: Request, job_id: int, user = Depends(require_api_key)):
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
            
            # Se for metanálise e tiver dados_extras com artigos, incluir artigos na resposta
            if job.get("dados_extras"):
                try:
                    dados_extras = json.loads(job["dados_extras"]) if isinstance(job["dados_extras"], str) else job["dados_extras"]
                    if isinstance(dados_extras, dict) and "artigos" in dados_extras:
                        response["artigos"] = dados_extras["artigos"]
                        response["total_artigos"] = dados_extras.get("total_artigos", len(dados_extras.get("artigos", [])))
                except:
                    pass  # Se não conseguir parsear, ignora

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

@api_router.post("/explicar")
@api_router.post("/explain_concept")
@limiter.limit("10 per minute")
def rota_explicar(request: Request, data: InputTexto, user = Depends(require_api_key)):
    log_t("INICIO REQUEST")
    print(">>> ENTROU NA ROTA /explicar")
    try:
        if not data.trecho:
            raise HTTPException(status_code=400, detail="Campo 'trecho' é obrigatório")

        custo = consumir_creditos(user["id"], "explicar")

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

@api_router.post("/critica")
@api_router.post("/critical_analysis")
@limiter.limit("10 per minute")
def rota_critica(request: Request, data: InputCritica, user = Depends(require_api_key)):
    try:
        foco_analise = data.foco_analise or "geral"
        custo = consumir_creditos(user["id"], "critica")

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

@api_router.post("/fatos")
@api_router.post("/fact_checker")
@limiter.limit("10 per minute")
def rota_fatos(request: Request, data: InputFatos, user = Depends(require_api_key)):
    try:
        custo = consumir_creditos(user["id"], "fatos")

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

@api_router.post("/mapa")
@api_router.post("/structure_visualizer")
@limiter.limit("10 per minute")
def rota_mapa(request: Request, data: InputMapa, user = Depends(require_api_key)):
    try:
        custo = consumir_creditos(user["id"], "mapa")

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

@api_router.post("/structure_mapper")
@limiter.limit("10 per minute")
def rota_structure_mapper(request: Request, data: InputMapa, user = Depends(require_api_key)):
    try:
        custo = consumir_creditos(user["id"], "structure_mapper")

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

@api_router.post("/meta_analysis/upload_articles")
@limiter.limit("5 per minute")
async def rota_upload_artigos_metanalise(
    request: Request, 
    files: list[UploadFile] = File(..., description="Lista de arquivos PDF/DOCX (máx. 15)"),
    user = Depends(require_api_key)
):
    """
    Endpoint para upload múltiplo de artigos científicos para metanálise.
    Aceita até 15 arquivos PDF/DOCX e faz análise PRISMA de cada um.
    """
    try:
        # Validar número de arquivos
        if len(files) > 15:
            raise HTTPException(
                status_code=400, 
                detail="Máximo de 15 artigos permitidos"
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
                    detail=f"Formato inválido: {file.filename}. Apenas PDF e DOCX são suportados."
                )
        
        # Cobrar créditos (custo por arquivo + análise PRISMA por artigo)
        custo_por_arquivo = 5  # pdf
        custo_analise_prisma = 15  # meta_etapa por artigo
        custo_total = (custo_por_arquivo + custo_analise_prisma) * len(files)
        consumir_creditos_total(user["id"], custo_total, "meta_analise_upload")
        
        # Importar módulos necessários (compatível com uvicorn api:app a partir de /app/backend)
        # read_docx já está definido neste módulo (api.py)
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
                
                # Salvar arquivo temporário
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
                    
                    # Extrair título (primeiras linhas ou usar nome do arquivo)
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
                    # Limpar arquivo temporário
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

        # Criar job assíncrono
        dados_extras_json = json.dumps(dados_extras) if dados_extras else None
        entrada_texto = data.texto_artigo if data.texto_artigo else (data.tema if data.tema else "Metanálise")
        job_id = db_insert_return_id(
            "INSERT INTO research_jobs (usuario_id, modulo, status, entrada, creditos, dados_extras) VALUES (%s, %s, %s, %s, %s, %s)",
            (user["id"], "meta_analise", "processing", entrada_texto, custo, dados_extras_json)
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

@api_router.post("/pdf")
@limiter.limit("10 per minute")
async def rota_pdf(request: Request, file: UploadFile = File(...), user = Depends(require_api_key)):
    try:
        if not file.filename or not file.filename.lower().endswith((".pdf", ".docx")):
            raise HTTPException(status_code=400, detail="Formato inválido. Apenas PDF e DOCX são suportados.")

        # Cobrar créditos antes de processar
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
                raise HTTPException(status_code=400, detail="Formato não suportado")
            
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
    """Texto a ser traduzido para português (usado pelo botão Traduzir texto)."""
    texto: str


@api_router.post("/traducao")
@limiter.limit("20 per minute")
def rota_traducao(request: Request, data: TraducaoInput, user=Depends(require_api_key)):
    """
    Traduz o texto extraído para português brasileiro (Qwen/Groq quando disponível).
    Usado quando o usuário clica em "Traduzir texto" na aba do texto extraído.
    """
    if not data.texto or not data.texto.strip():
        raise HTTPException(status_code=400, detail="Texto não pode estar vazio")
    try:
        resultado_pt = obter_versao_portugues(data.texto.strip())
        return {"resultado_pt": resultado_pt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao traduzir: {str(e)}")


@api_router.post("/chat-followup")
@limiter.limit("20 per minute")
def rota_chat_followup(request: Request, data: ChatFollowUpInput, user = Depends(require_api_key)):
    """
    Processa mensagens de follow-up do chat, permitindo interação com respostas da IA.
    """
    try:
        if not data.mensagem or not data.mensagem.strip():
            raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia")

        custo = consumir_creditos(user["id"], "chat_followup")

        # Construir contexto do histórico
        contexto_historico = ""
        if data.historico:
            for msg in data.historico[-5:]:  # Últimas 5 mensagens para contexto
                role = "Usuário" if msg.get("role") == "user" else "Assistente"
                contexto_historico += f"{role}: {msg.get('content', '')}\n\n"

        # Construir prompt contextualizado baseado no tipo de análise
        tipo_analise_nomes = {
            "explicar": "Explicação de Conceito",
            "critica": "Análise Crítica",
            "fatos": "Verificação de Fatos",
            "mapa": "Mapa Conceitual",
            "structure_mapper": "Mapeamento de Estrutura",
            "meta_analise": "Metanálise",
        }
        
        nome_analise = tipo_analise_nomes.get(data.tipo_analise, data.tipo_analise)

        prompt = f"""Você é um assistente especializado em análise científica. O usuário está interagindo com uma análise do tipo: {nome_analise}.

Contexto da análise anterior:
{contexto_historico if contexto_historico else "Esta é a primeira interação após a análise inicial."}

Texto do artigo (referência):
{data.texto_artigo[:2000] if data.texto_artigo else "Não disponível"}

Mensagem do usuário:
{data.mensagem}

Responda de forma clara, objetiva e útil. Se o usuário pedir melhorias, sugestões ou esclarecimentos, forneça respostas práticas e acionáveis. Mantenha o foco no contexto científico e na análise realizada."""

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

        resposta = gerar_resposta(prompt, temperatura=0.7)  # Usa padrão configurado (1000 tokens)

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
# ✅ INCLUIR ROUTERS NA APLICAÇÃO
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

# Checkout créditos (POST /genapi/checkout/creditos)
try:
    from backend.routes.checkout_creditos import router as checkout_router
except ImportError:
    try:
        from routes.checkout_creditos import router as checkout_router
    except ImportError:
        from .routes.checkout_creditos import router as checkout_router
app.include_router(checkout_router)

# Log para debug: verificar se os routers foram incluídos
logging.warning(f"[DEBUG] Router incluído com prefixo: /genapi")
logging.warning(f"[DEBUG] Total de rotas após incluir routers: {len(app.routes)}")

# ============================================
# ✅ EXECUÇÃO LOCAL (para desenvolvimento)
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

