# 🔧 Corrigir Erro "ModuleNotFoundError: No module named 'your_application'"

## ❌ Problema

O Render está tentando executar:
```
gunicorn your_application.wsgi
```

Mas o correto é:
```
cd backend && gunicorn api:app --bind 0.0.0.0:$PORT
```

## ✅ Solução

### Opção 1: Usar o render.yaml (Recomendado)

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Selecione seu serviço `medquest-research-api`
3. Vá em **Settings** → **Build & Deploy**
4. Em **Build Command**, certifique-se de que está:
   ```
   pip install -r backend/requirements.txt
   ```
5. Em **Start Command**, certifique-se de que está:
   ```
   cd backend && gunicorn api:app --bind 0.0.0.0:$PORT
   ```
6. **IMPORTANTE**: Se houver um campo "Auto-Deploy", certifique-se de que está usando o `render.yaml`
7. Salve as alterações
8. Faça um **Manual Deploy** ou aguarde o próximo deploy automático

### Opção 2: Configuração Manual

Se o `render.yaml` não estiver sendo detectado:

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Selecione seu serviço
3. Vá em **Settings** → **Build & Deploy**
4. **Build Command**:
   ```
   pip install -r backend/requirements.txt
   ```
5. **Start Command**:
   ```
   cd backend && gunicorn api:app --bind 0.0.0.0:$PORT
   ```
6. Salve e faça um novo deploy

## 🔍 Verificação

Após o deploy, verifique os logs:

1. Vá em **Logs** no painel do Render
2. Procure por mensagens como:
   - ✅ `[INFO] Starting gunicorn`
   - ✅ `Listening at: http://0.0.0.0:XXXX`
   - ❌ `ModuleNotFoundError` (não deve aparecer)

## 📝 Nota

O arquivo `render.yaml` na raiz do projeto já está configurado corretamente:
- **Build**: `pip install -r backend/requirements.txt`
- **Start**: `cd backend && gunicorn api:app --bind 0.0.0.0:$PORT`

Se o Render não estiver usando o `render.yaml` automaticamente, configure manualmente usando os comandos acima.

