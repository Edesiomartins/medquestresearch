# Dockerfile para Railway
# Usa requirements.txt da raiz (que é idêntico ao backend/requirements.txt)
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt da raiz PRIMEIRO e instalar dependências
# Isso resolve o problema do Railpack tentar instalar antes de copiar os arquivos
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copiar o diretório backend
COPY backend/ /app/backend/

# Expor porta (Railway define $PORT automaticamente)
EXPOSE 8000

# Comando de inicialização
# Railway injeta $PORT como variável de ambiente
WORKDIR /app/backend
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
