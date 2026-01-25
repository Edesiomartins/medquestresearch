# Remover Start Command no Railway

## Problema

Erro ao subir o container: **"The executable `cd` could not be found"**.

Alguma configuração está passando um comando com `cd` (ex.: `cd backend && uvicorn ...`). O Railway tenta rodar `cd` como executável; `cd` é comando do shell, não um binário.

**Origens possíveis do `cd`:**

1. **Start Command** no **painel do Railway** (Settings → Deploy/Service)
2. **Procfile** na raiz — se existir `web: cd backend && ...`, o Railway pode usá‑lo e sobrescrever o `CMD` do Dockerfile. **Solução:** remover o `Procfile` quando se usa Dockerfile.
3. **nixpacks.toml** — `[start] cmd = "cd backend && ..."` pode ser lido em alguns fluxos. **Solução:** remover o bloco `[start]` ao usar o builder DOCKERFILE.

## O que fazer

### 1. Abrir o serviço no Railway

1. Acesse [railway.app](https://railway.app) e abra seu **projeto**
2. Clique no **serviço do backend** (a caixa do deploy)

### 2. Achar e limpar o Start Command

1. Clique em **Settings** (ou no ícone de engrenagem)
2. Procure a seção **Deploy** ou **Start** ou **Service**
3. Encontre o campo **Start Command** ou **Custom Start Command** ou **Override Start Command**
4. **Apague todo o conteúdo** (ex.: `cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT`)
5. Deixe o campo **em branco** / vazio
6. Salve (Save / Deploy / Apply se houver)

### 3. Redeploy

1. Vá em **Deployments**
2. Clique nos **três pontos (⋯)** do último deploy
3. Escolha **Redeploy**

Ou dispare um novo deploy (por exemplo, com um novo commit e push).

---

## Depois de limpar

Com o Start Command **vazio**, o Railway passa a usar o **`CMD` do Dockerfile**:

```dockerfile
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

O `WORKDIR` no Dockerfile já é `/app/backend`, então o `uvicorn` encontra `api.py` sem precisar de `cd`.

---

## Onde costuma estar no painel

- **Settings** → **Deploy** → **Start Command**  
- **Settings** → **Service** → **Start Command**  
- **Variables** → às vezes há variável tipo `START_COMMAND` (se existir, apague o valor ou a variável)

O nome exato pode variar com a versão do painel do Railway.
