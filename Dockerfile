# Dockerfile para Railway (alternativa ao nixpacks)
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Expor porta (Railway define $PORT)
EXPOSE $PORT

# Comando de inicialização
WORKDIR /app/backend
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
