# Erro: "/backend" not found no build do Dockerfile

## Causa

O erro acontece quando o **Root Directory** do serviço no Railway está definido como `backend` (ou outro subdiretório). Nesse caso, o contexto de build é só a pasta `backend/`, e não existe um subdiretório `backend/` dentro dele. O `COPY backend/` no Dockerfile falha porque `backend/` não existe nesse contexto.

## O que fazer no Railway

1. Abra o **projeto** no Railway e selecione o **serviço do backend**.
2. Vá em **Settings** (ou **Config**).
3. Procure **Root Directory** (ou **Source** / **Build**).
4. Deixe **Root Directory em branco** (ou use `.` / raiz do repositório).

Assim o contexto de build passa a ser a raiz do repositório e o `COPY backend/` do Dockerfile encontra a pasta `backend/`.

## Onde fica no painel

- **Settings** → **Build** → **Root Directory** → deixe vazio.  
ou  
- **Settings** → **Source** → **Root Directory** → deixe vazio.

## Depois de ajustar

1. Salve as alterações.
2. Em **Deployments**, faça **Redeploy** (ou dispare um novo deploy).

O build deve passar, pois o contexto incluirá a raiz do repo e a pasta `backend/`.
