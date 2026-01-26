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

- ✅ `https://medquestresearch.up.railway.app` (frontend)
- ✅ `https://medquestresearch-api.up.railway.app` (API)
- ✅ `https://medquestresearch-production.up.railway.app`
- ✅ `http://localhost:3000`, `http://127.0.0.1:3000`
- ✅ `http://localhost:3001`, `http://127.0.0.1:3001`
- ✅ **Regex:** qualquer `https://*.up.railway.app` (deploys com URL gerada)

## 404 + CORS "falta Access-Control-Allow-Origin"

Se a requisição retorna **404** e o navegador acusa CORS, em muitos casos o **backend não está respondendo** (container não subiu ou deploy falhou). Respostas 404/502 da infra do Railway **não** passam pelo FastAPI, então **não recebem cabeçalhos CORS**.

**Alteração recente:** o `database.py` **não** quebra mais no import se `DATABASE_URL` estiver vazio. A API sobe e **`/` e `/health` passam a responder**. Assim você consegue distinguir:
- **404/502 em `/` ou `/health`** → backend não subiu (veja logs, `railway.json`, Start Command, etc.).
- **200 em `/` ou `/health`** → backend no ar; se `/login` der 404 ou 500 **com** aviso de CORS, a resposta já vem do FastAPI (com CORS). Se ainda "falta Access-Control-Allow-Origin" em `/login`, confira a origem do frontend (precisa bater com `ALLOWED_ORIGINS` ou o regex `*.up.railway.app`).

**O que fazer:**
1. No Railway, verificar se o **deploy do backend** está **sucesso** (verde) e o container está rodando.
2. Abrir `https://medquestresearch-api.up.railway.app/` ou `https://medquestresearch-api.up.railway.app/health` no navegador. Se der 404/502, o backend não está no ar.
3. Conferir **Variables**: `DATABASE_URL` (vínculo com Postgres ou URL) e `API_OPENAI_KEY_RESEARCH`. Conferir **Start Command** vazio para usar o `CMD` do Dockerfile.
4. Ver os **logs** do serviço (erro de import, `cd`, conexão com o banco, etc.) e corrigir.
5. Depois que `/` ou `/health` responder 200, testar `/login` de novo; as respostas do FastAPI (incluindo 401, 404, 500) já vêm com CORS.

## 🔴 Frontend chamando a URL **errada** (medquest-**r**esearch-api)

Se o navegador mostra requisições para **`https://medquest-research-api.up.railway.app`** (com hífen: *medquest-**r**esearch-api*) e 404 + CORS, o frontend está usando a **URL antiga**. A API que está no ar é:

- **`https://medquestresearch-api.up.railway.app`** (sem hífen: *medquestresearch-api*)

O Next.js grava `NEXT_PUBLIC_API_BASE_URL` no **build**. Se no Railway a variável do **frontend** estiver com a URL antiga, o build fica errado.

**O que fazer:**

1. No Railway, abra o **serviço do frontend** (não o da API).
2. Vá em **Variables**.
3. Ajuste **`NEXT_PUBLIC_API_BASE_URL`** para:  
   `https://medquestresearch-api.up.railway.app`  
   (remova ou corrija se estiver `medquest-research-api`).
4. Faça **Redeploy** do frontend (ou um novo **Deploy** com push) para rodar um **build novo**. Só redeploy sem rebuild pode manter a URL antiga.
5. Confira no navegador (DevTools → Network) que as chamadas vão para `medquestresearch-api.up.railway.app`.

---

## ⚠️ Importante

- As URLs são combinadas (defaults + variável de ambiente).
- Regex cobre qualquer subdomínio `*.up.railway.app`.
- URLs devem incluir o protocolo (`https://` ou `http://`).
