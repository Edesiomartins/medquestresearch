# Solução definitiva: erro `backend/requirements.txt` no Railway

## Causa do erro

O Railway está usando o **Railpack** (não o Dockerfile) e o Railpack injeta automaticamente este comando na fase **build**:

```bash
pip install -r backend/requirements.txt
```

Esse comando falha porque, no contexto e na ordem em que o Railpack roda o build, o arquivo `backend/requirements.txt` ainda **não existe** no momento em que o comando é executado.

## O que foi feito no projeto

### 1. `railpack.json` criado

Foi criado um `railpack.json` na raiz do repositório com:

```json
{
  "$schema": "https://schema.railpack.com",
  "steps": {
    "build": {
      "commands": []
    }
  }
}
```

Isso **substitui** os comandos da fase `build` do Railpack. A fase `build` fica vazia, então o comando `pip install -r backend/requirements.txt` deixa de ser executado.

As dependências continuam sendo instaladas na fase **install**, que usa `pip install -r requirements.txt` (arquivo da raiz, que existe nessa etapa).

### 2. Uso do Dockerfile (alternativa)

O `railway.json` e o `railway.toml` estão configurados para:

```json
"builder": "DOCKERFILE",
"dockerfilePath": "Dockerfile"
```

Ou seja, a intenção é usar o **Dockerfile** em vez do Railpack. Se o Railway estiver respeitando essa configuração, o build usa apenas o Dockerfile e o `pip install -r backend/requirements.txt` do Railpack não é executado.

## O que fazer no Railway

### Opção A: Garantir que o Dockerfile seja usado

1. No painel do Railway: projeto → serviço do **backend**.
2. Aba **Variables**:
   - Se existir `RAILWAY_DOCKERFILE_PATH`, defina:
     - `RAILWAY_DOCKERFILE_PATH=Dockerfile`
   - Ou remova essa variável para usar o `Dockerfile` na raiz.
3. Em **Settings** → **Build**:
   - **Builder**: escolha **Dockerfile** (e não Railpack/Nixpacks), se a interface permitir.
   - **Root Directory**: deixe **vazio** (raiz do repositório), para que o `Dockerfile` na raiz seja encontrado.
4. **Deployments** → **Redeploy** (ou **Clear Build Cache** em **Settings** → **Build** e depois um novo deploy).

Se o build for feito com Dockerfile, os logs devem mostrar algo como:

```text
==========================Using detected Dockerfile!==========================
```

e não:

```text
load build definition from railpack-plan.json
```

### Opção B: Continuar com Railpack + `railpack.json`

Se o Railway continuar usando Railpack:

1. Mantenha o `railpack.json` na raiz (já criado no projeto).
2. Faça commit e push e dispare um novo deploy.

Com `"build": { "commands": [] }`, a fase `build` fica vazia e o `pip install -r backend/requirements.txt` deixa de ser executado. O `pip install -r requirements.txt` da fase **install** continua responsável por instalar as dependências.

## Resumo

| Causa | Ação no projeto | O que fazer no Railway |
|-------|------------------|-------------------------|
| Railpack injeta `pip install -r backend/requirements.txt` na fase **build** | `railpack.json` com `"build": { "commands": [] }` | — |
| Railway não está usando o Dockerfile | `railway.json` / `railway.toml` com `builder: DOCKERFILE` | Ajustar **Builder** e **Root Directory** em **Settings** → **Build** e, se precisar, `RAILWAY_DOCKERFILE_PATH` |

Com o `railpack.json` no repositório e, se possível, o build configurado para usar o **Dockerfile** no painel, o erro `Could not open requirements file: backend/requirements.txt` tende a desaparecer.
