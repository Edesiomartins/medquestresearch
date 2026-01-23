#!/bin/bash
# Script de build para Railway
# Garante que requirements.txt esteja disponível em ambos os locais

set -e

# Copiar requirements.txt da raiz para backend/ se não existir
if [ -f requirements.txt ] && [ ! -f backend/requirements.txt ]; then
    cp requirements.txt backend/requirements.txt
fi

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

echo "Build concluído com sucesso!"
