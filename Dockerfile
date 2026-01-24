FROM python:3.12-slim

WORKDIR /app

# Copiar requirements.txt da raiz
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar backend
COPY backend/ ./backend/

EXPOSE 8000

WORKDIR /app/backend
# Usar shell para expandir $PORT (Railway injeta PORT). Exec form não expande ${PORT:-8000}.
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
