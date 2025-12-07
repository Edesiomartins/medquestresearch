# ============================================
# ✅ IMPORTS E CONFIGURAÇÕES INICIAIS
# ============================================

import sys
import os
import hashlib
import secrets
import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

# Banco de dados
from database import db_select, db_select_one, db_execute

# Módulos internos de IA (arquivos reais enviados)
from explain_concept import explicar_conceito
from critical_analysis import aplicar_leitura_critica
from Fact_checker import verificar_fatos
from Perspective_research import buscar_perspectivas_pubmed
from structure_visualizer import gerar_mapa_visual
from pdf_processor import extrair_texto_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================
# ✅ APLICAÇÃO FLASK
# ============================================

app = Flask(__name__)
CORS(app)


# ============================================
# ✅ FUNÇÕES AUXILIARES (TOKEN, AUTENTICAÇÃO, LOGS)
# ============================================

def gerar_token():
    return secrets.token_hex(32)


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def autenticar(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        return None

    row = db_select_one(
        "SELECT * FROM gen_usuarios WHERE token=%s",
        (token,)
    )
    return row


def debitar_creditos(usuario_id, quantia):
    user = db_select_one("SELECT * FROM gen_usuarios WHERE id=%s", (usuario_id,))
    if not user:
        return False

    if user["creditos"] < quantia:
        return False

    db_execute("""
        UPDATE gen_usuarios
        SET creditos = creditos - %s,
            creditos_usados = creditos_usados + %s
        WHERE id=%s
    """, (quantia, quantia, usuario_id))

    return True


def registrar_log(usuario_id, modulo, entrada, saida, creditos):
    ip = request.remote_addr
    db_execute("""
        INSERT INTO gen_logs_uso (usuario_id, modulo, entrada, saida, creditos_gastos, ip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (usuario_id, modulo, entrada, saida, creditos, ip))


# ============================================
# ✅ ROTAS BÁSICAS
# ============================================

@app.route("/")
def index():
    return jsonify({"status": "MedQuestGen API está ativa ✅"})


@app.route("/ping")
def ping():
    return jsonify({"message": "pong"})


# ============================================
# ✅ ROTAS DE USUÁRIO (CADASTRO / LOGIN / CRÉDITOS)
# ============================================

@app.route("/cadastro", methods=["POST"])
def cadastro():
    data = request.json
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    if not nome or not email or not senha:
        return jsonify({"erro": "Campos obrigatórios faltando"}), 400

    if db_select_one("SELECT * FROM gen_usuarios WHERE email=%s", (email,)):
        return jsonify({"erro": "Email já cadastrado"}), 400

    senha_hash = hash_senha(senha)
    token = gerar_token()

    db_execute("""
        INSERT INTO gen_usuarios (nome, email, senha_hash, token, creditos)
        VALUES (%s, %s, %s, %s, %s)
    """, (nome, email, senha_hash, token, 50))

    return jsonify({"status": "Usuário criado", "token": token})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    row = db_select_one("SELECT * FROM gen_usuarios WHERE email=%s", (email,))
    if not row:
        return jsonify({"erro": "Email não encontrado"}), 404

    if row["senha_hash"] != hash_senha(senha):
        return jsonify({"erro": "Senha incorreta"}), 401

    token = gerar_token()
    db_execute("UPDATE gen_usuarios SET token=%s WHERE id=%s", (token, row["id"]))

    return jsonify({"token": token})


@app.route("/creditos", methods=["GET"])
def creditos():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    return jsonify({
        "creditos": user["creditos"],
        "creditos_usados": user["creditos_usados"]
    })


# ============================================
# ✅ ROTAS DE IA — EXPLICAR
# ============================================

@app.route("/explicar", methods=["POST"])
def rota_explicar():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    data = request.json
    texto_artigo = data.get("texto_artigo")
    trecho = data.get("trecho")
    nivel = data.get("nivel", "graduação")

    if not texto_artigo or not trecho:
        return jsonify({"erro": "Envie texto_artigo e trecho"}), 400

    custo = 5
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    resposta = explicar_conceito(texto_artigo, trecho, nivel)
    registrar_log(user["id"], "explicar", texto_artigo, resposta, custo)

    return jsonify({"resultado": resposta})


# ============================================
# ✅ LEITURA CRÍTICA
# ============================================

@app.route("/critica", methods=["POST"])
def rota_critica():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    data = request.json
    texto_artigo = data.get("texto_artigo")

    if not texto_artigo:
        return jsonify({"erro": "Envie texto_artigo"}), 400

    custo = 7
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    resposta = aplicar_leitura_critica(texto_artigo)
    registrar_log(user["id"], "critica", texto_artigo, resposta, custo)

    return jsonify({"resultado": resposta})


# ============================================
# ✅ VERIFICAR FATOS
# ============================================

@app.route("/fatos", methods=["POST"])
def rota_fatos():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    data = request.json
    texto_artigo = data.get("texto_artigo")

    if not texto_artigo:
        return jsonify({"erro": "Envie texto_artigo"}), 400

    custo = 5
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    resposta = verificar_fatos(texto_artigo)
    registrar_log(user["id"], "fatos", texto_artigo, resposta, custo)

    return jsonify({"resultado": resposta})


# ============================================
# ✅ PERSPECTIVA CIENTÍFICA / PUBMED
# ============================================

@app.route("/perspectiva", methods=["POST"])
def rota_perspectiva():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    data = request.json
    texto_artigo = data.get("texto_artigo")

    if not texto_artigo:
        return jsonify({"erro": "Envie texto_artigo"}), 400

    custo = 10
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    resposta = buscar_perspectivas_pubmed(texto_artigo)
    registrar_log(user["id"], "perspectiva", texto_artigo, resposta, custo)

    return jsonify({"resultado": resposta})


# ============================================
# ✅ MAPA MENTAL
# ============================================

@app.route("/mapa", methods=["POST"])
def rota_mapa():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    data = request.json
    texto_artigo = data.get("texto_artigo")

    if not texto_artigo:
        return jsonify({"erro": "Envie texto_artigo"}), 400

    custo = 8
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    resposta = gerar_mapa_visual(texto_artigo)
    registrar_log(user["id"], "mapa", texto_artigo, resposta, custo)

    return jsonify({"resultado": resposta})


# ============================================
# ✅ PROCESSAR PDF (USANDO extrair_texto_pdf)
# ============================================

@app.route("/pdf", methods=["POST"])
def rota_pdf():
    user = autenticar(request)
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    if "file" not in request.files:
        return jsonify({"erro": "Arquivo PDF não enviado"}), 400

    arquivo = request.files["file"]

    # verifica extensão
    if not arquivo.filename.lower().endswith(".pdf"):
        return jsonify({"erro": "Envie um arquivo PDF válido"}), 400

    # custo
    custo = 12
    if not debitar_creditos(user["id"], custo):
        return jsonify({"erro": "Créditos insuficientes"}), 402

    # salvar temporariamente
    temp_path = f"/home/dredesiomartins/MedquestGen/backend/_temp_{secrets.token_hex(6)}.pdf"
    arquivo.save(temp_path)

    try:
        # processar
        texto_extraido = extrair_texto_pdf(temp_path)

        registrar_log(
            user["id"],
            "pdf",
            "[ARQUIVO PDF]",
            texto_extraido[:5000],  # evita log gigante
            custo
        )

        return jsonify({"resultado": texto_extraido})

    except Exception as e:
        return jsonify({"erro": "Falha ao processar PDF", "detalhes": str(e)}), 500

    finally:
        # remover arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
