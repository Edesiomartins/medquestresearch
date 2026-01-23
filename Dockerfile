# Dockerfile para Railway
# Agora o requirements.txt está dentro do diretório backend/
FROM python:3.12-slim

WORKDIR /app

# Copiar o diretório backend (que contém requirements.txt)
COPY backend/ /app/backend/

# Instalar dependências do backend/requirements.txt
WORKDIR /app/backend
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expor porta (Railway define $PORT automaticamente)
EXPOSE 8000

# Comando de inicialização
# Railway injeta $PORT como variável de ambiente
WORKDIR /app/backend
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
