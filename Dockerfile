# Dockerfile para Railway
# Este Dockerfile resolve o problema do Railpack tentar instalar de backend/requirements.txt
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt da raiz e instalar dependências
# IMPORTANTE: Usa apenas requirements.txt da raiz, não backend/requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código (incluindo backend/)
COPY . .

# Expor porta (Railway define $PORT automaticamente)
EXPOSE 8000

# Comando de inicialização
# Railway injeta $PORT como variável de ambiente
WORKDIR /app/backend
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
