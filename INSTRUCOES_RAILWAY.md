# 🚨 INSTRUÇÕES URGENTES - Configurar Railway Manualmente

## ⚠️ IMPORTANTE: O Railway está ignorando a configuração automática

O Railway está usando **Railpack** automaticamente mesmo com os arquivos de configuração. Você **DEVE** configurar manualmente no painel.

## 🔧 Passos OBRIGATÓRIOS

### 1. No Painel do Railway

1. Acesse [railway.app](https://railway.app)
2. Selecione seu projeto (backend)
3. Vá em **Settings** → **Build**

### 2. Configurar Builder

1. Em **Builder**, selecione **DOCKERFILE** (não Railpack, não Nixpacks)
2. Em **Dockerfile Path**, deixe como `Dockerfile` (ou vazio)
3. **Clique em Save**

### 3. Limpar Cache

1. Ainda em **Settings** → **Build**
2. Clique em **Clear Build Cache**
3. Isso força um rebuild completo

### 4. Redeploy

1. Vá em **Deployments**
2. Clique nos três pontos (⋯) do último deploy
3. Selecione **Redeploy**

## ✅ Verificação

Após o redeploy, verifique os logs. Deve aparecer:

```
Step 1/6 : FROM python:3.12-slim
Step 2/6 : WORKDIR /app
Step 3/6 : COPY requirements.txt /app/requirements.txt
Step 4/6 : RUN pip install -r /app/requirements.txt
```

**NÃO deve** aparecer:
```
pip install -r backend/requirements.txt  ❌
```

## 🔍 Por que isso acontece?

O Railway tem detecção automática que pode ignorar arquivos de configuração (`railway.toml`, `railway.json`) se:
- O builder não estiver configurado manualmente no painel
- O cache ainda tiver informações do build anterior com Railpack
- O Railway detectar Python e tentar usar Railpack automaticamente

## 📝 Arquivos Modificados

- ✅ `Dockerfile` - Otimizado para usar apenas `requirements.txt` da raiz
- ✅ `.dockerignore` - Criado para ignorar arquivos desnecessários
- ✅ `nixpacks.toml` - Renomeado para `nixpacks.toml.bak` (não será usado)
- ✅ `railway.toml` - Configurado para Dockerfile
- ✅ `railway.json` - Configurado para Dockerfile

## ⚠️ Se Ainda Não Funcionar

1. Verifique se o Builder está realmente como **DOCKERFILE** no painel
2. Limpe o cache novamente
3. Faça um novo redeploy
4. Verifique os logs completos do build

## 🆘 Suporte

Se mesmo após seguir todos os passos o erro persistir:
- Verifique se o `Dockerfile` está na raiz do projeto
- Verifique se o `requirements.txt` está na raiz do projeto
- Entre em contato com o suporte do Railway
