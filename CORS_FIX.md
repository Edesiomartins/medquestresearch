# 🔧 Correção de CORS - Railway

## ❌ Problema

Erro de CORS ao fazer requisições do frontend para o backend:
```
CORS Missing Allow Origin
Requisição cross-origin bloqueada
```

## ✅ Solução Implementada

O código do backend foi atualizado para incluir automaticamente:
- `https://medquestresearch.up.railway.app` (frontend Railway)
- `http://localhost:3000` (desenvolvimento local)
- `http://localhost:3001` (desenvolvimento local alternativo)

## 🔧 Configuração no Railway

### Opção 1: Usar Defaults (Recomendado)

O backend já inclui as URLs principais por padrão. **Não é necessário** configurar `ALLOWED_ORIGINS` se você estiver usando:
- Frontend em `medquestresearch.up.railway.app`

### Opção 2: Configurar Manualmente

Se precisar adicionar URLs adicionais, configure no Railway:

1. No painel do Railway (backend), vá em **Variables**
2. Adicione a variável:
   ```
   ALLOWED_ORIGINS=https://medquestresearch.up.railway.app,https://outra-url.com
   ```
3. Separe múltiplas URLs por vírgula (sem espaços)

## 🔍 Verificação

Após fazer commit e push:

1. O Railway fará redeploy automaticamente
2. Teste uma requisição do frontend
3. O erro de CORS deve desaparecer

## 📝 URLs Incluídas por Padrão

- ✅ `https://medquestresearch.up.railway.app`
- ✅ `https://medquest-research.up.railway.app`
- ✅ `https://medquestresearch-production.up.railway.app`
- ✅ `http://localhost:3000`, `http://127.0.0.1:3000`
- ✅ `http://localhost:3001`, `http://127.0.0.1:3001`
- ✅ **Regex:** qualquer `https://*.up.railway.app` (deploys com URL gerada)

## 404 + CORS "falta Access-Control-Allow-Origin"

Se a requisição retorna **404** e o navegador acusa CORS, em muitos casos o **backend não está respondendo** (container não subiu ou deploy falhou). Respostas 404/502 da infra do Railway **não** passam pelo FastAPI, então **não recebem cabeçalhos CORS**.

**O que fazer:**
1. No Railway, verificar se o **deploy do backend** está **sucesso** (verde) e o container está rodando.
2. Testar `https://medquest-research-api.up.railway.app/` ou `/health` no navegador. Se der 404/502, o backend não está no ar.
3. Conferir logs do serviço no Railway (erro de `cd`, import, variável de ambiente, etc.) e corrigir o deploy.
4. Depois que `/` ou `/health` responder, o `/login` e as demais rotas também devem responder e o CORS passará a funcionar.

## ⚠️ Importante

- As URLs são combinadas (defaults + variável de ambiente).
- Regex cobre qualquer subdomínio `*.up.railway.app`.
- URLs devem incluir o protocolo (`https://` ou `http://`).
