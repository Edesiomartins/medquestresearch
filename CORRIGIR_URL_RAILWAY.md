# 🔧 Como Corrigir a URL da API no Railway

## ⚠️ Problema

O frontend está chamando a URL antiga: `https://medquest-research-api.up.railway.app` (com hífen)

A URL correta é: `https://medquestresearch-api.up.railway.app` (sem hífen)

## ✅ Solução Passo a Passo

### 1. Acesse o Railway Dashboard
- Vá para: https://railway.app
- Faça login na sua conta

### 2. Abra o Serviço do Frontend
- Clique no projeto **MedQuestResearch**
- Clique no serviço do **Frontend** (não o da API)

### 3. Vá em Variables (Variáveis de Ambiente)
- No menu lateral, clique em **Variables**
- Procure pela variável: `NEXT_PUBLIC_API_BASE_URL`

### 4. Corrija a URL
- Se a variável estiver com: `https://medquest-research-api.up.railway.app`
- Altere para: `https://medquestresearch-api.up.railway.app`
- **IMPORTANTE:** Remova o hífen entre "medquest" e "research"

### 5. Salve e Faça Redeploy
- Clique em **Save** ou **Update**
- Vá em **Settings** → **Redeploy** (ou faça um novo commit/push)
- **CRÍTICO:** O Next.js precisa fazer um **novo build** para embutir a nova URL

### 6. Verifique o Build
- Vá em **Deployments** e aguarde o novo deploy completar
- Verifique os logs para confirmar que o build foi feito com a URL correta

## 🔍 Como Verificar se Está Correto

### Opção 1: Verificar no Console do Navegador
1. Abra o DevTools (F12)
2. Vá na aba **Console**
3. Você deve ver: `🔗 API Base URL: https://medquestresearch-api.up.railway.app`
4. Se ainda aparecer a URL antiga, o build não foi atualizado

### Opção 2: Verificar nas Requisições
1. Abra o DevTools (F12)
2. Vá na aba **Network**
3. Faça uma requisição (ex: login)
4. Verifique se a URL da requisição é: `https://medquestresearch-api.up.railway.app/genapi/...`
5. Se ainda aparecer `medquest-research-api`, o build precisa ser refeito

## 🚨 Se o Problema Persistir

### 1. Limpar Cache do Build
- No Railway, vá em **Settings** do frontend
- Procure por opções de cache
- Limpe o cache e faça um novo deploy

### 2. Forçar Novo Build
- Faça um commit vazio: `git commit --allow-empty -m "force rebuild"`
- Faça push: `git push`
- Isso força o Railway a fazer um novo build completo

### 3. Verificar Variáveis de Ambiente
- Confirme que `NEXT_PUBLIC_API_BASE_URL` está definida corretamente
- Verifique se não há espaços extras ou caracteres especiais
- A URL deve ser exatamente: `https://medquestresearch-api.up.railway.app`

## 📝 URLs Corretas do Projeto

- **Frontend:** `https://medquestresearch.up.railway.app`
- **API:** `https://medquestresearch-api.up.railway.app` ✅
- **❌ NÃO USE:** `https://medquest-research-api.up.railway.app` (URL antiga)

## 💡 Dica

O código agora tem uma correção automática que substitui a URL antiga pela correta, mas isso só funciona se o código for reconstruído. Por isso é **essencial** fazer um novo build após corrigir a variável de ambiente.
