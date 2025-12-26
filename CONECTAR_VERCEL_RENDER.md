# 🔗 Conectar Vercel (Frontend) ao Render (Backend)

## 📋 Pré-requisitos

✅ Backend deployado no Render e funcionando  
✅ URL do backend no Render (ex: `https://medquest-research-api.onrender.com`)

## 🚀 Passo a Passo

### 1. Obter a URL do Backend no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Selecione seu serviço `medquest-research-api`
3. A URL estará no topo da página
4. **Copie a URL completa** (ex: `https://medquest-research-api.onrender.com`)
   - ⚠️ **IMPORTANTE**: Sem barra no final
   - ⚠️ **IMPORTANTE**: Sem `/genapi` (o código adiciona automaticamente)

### 2. Configurar Variável no Vercel

1. **Acesse o Vercel Dashboard**
   - https://vercel.com/dashboard

2. **Selecione seu projeto MedQuestResearch**

3. **Vá em Settings → Environment Variables**

4. **Verifique se já existe `NEXT_PUBLIC_API_BASE_URL`**
   - Se existir, clique em **Edit**
   - Se não existir, clique em **Add New**

5. **Configure a variável:**
   - **Key**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: Cole a URL do Render (ex: `https://medquest-research-api.onrender.com`)
   - **Environments**: Marque todas as opções:
     - ✅ Production
     - ✅ Preview  
     - ✅ Development

6. **Clique em Save**

### 3. Fazer Redeploy no Vercel

⚠️ **CRÍTICO**: Variáveis de ambiente só são aplicadas em novos deploys!

1. Vá em **Deployments**
2. Clique nos **três pontos (⋯)** do último deploy
3. Selecione **Redeploy**
4. Aguarde o deploy completar (2-5 minutos)

### 4. Verificar se Funcionou

1. **Acesse sua aplicação no Vercel**
   - URL estará em **Deployments** → **Domains**

2. **Abra o Console do Navegador (F12)**
   - Vá na aba **Network** ou **Console**

3. **Teste fazer Login ou Upload de PDF**
   - As requisições devem ir para: `https://sua-url-render.onrender.com/genapi/...`
   - Não deve aparecer erro de CORS
   - Status deve ser 200 (sucesso)

## ✅ Exemplo de Configuração

### No Vercel (Environment Variables):

```
Key: NEXT_PUBLIC_API_BASE_URL
Value: https://medquest-research-api.onrender.com
```

### Como o Frontend Usa:

O código em `frontend/app/lib/api-config.ts` faz:
```typescript
// URL base do Render
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
// Exemplo: https://medquest-research-api.onrender.com

// Adiciona /genapi automaticamente
const fullUrl = `${API_BASE_URL}/genapi/login`;
// Resultado: https://medquest-research-api.onrender.com/genapi/login
```

## 🔍 Troubleshooting

### ❌ Erro: "NEXT_PUBLIC_API_BASE_URL não configurado"

**Causa**: Variável não configurada ou deploy antigo

**Solução**:
1. Verifique se a variável está no Vercel
2. Faça um **Redeploy** (variáveis só aplicam em novos builds)

### ❌ Erro: "CORS policy blocked"

**Causa**: Backend não está aceitando requisições do Vercel

**Solução**: 
- O CORS já está configurado no backend para aceitar todas as origens (`*`)
- Se persistir, verifique se o backend está rodando

### ❌ Erro: "404 Not Found"

**Causa**: URL incorreta ou backend não tem a rota

**Solução**:
1. Verifique se a URL está correta (sem barra no final)
2. Teste a URL diretamente: `https://sua-url.onrender.com/genapi/ping`
3. Deve retornar: `{"status": "ok"}`

### ❌ Requisições ainda vão para URL antiga

**Causa**: Cache do navegador ou deploy antigo

**Solução**:
1. Faça um novo deploy no Vercel
2. Limpe o cache do navegador (Ctrl+Shift+R)
3. Teste em aba anônima

## 📝 Checklist Final

- [ ] Backend deployado e funcionando no Render
- [ ] URL do backend copiada (sem barra no final)
- [ ] Variável `NEXT_PUBLIC_API_BASE_URL` configurada no Vercel
- [ ] Variável aplicada a todas as environments (Production, Preview, Development)
- [ ] Redeploy feito no Vercel
- [ ] Testado login/upload e funcionando
- [ ] Sem erros de CORS no console

## 🎯 Resultado Esperado

Após configurar corretamente:

✅ Frontend (Vercel) → Backend (Render)  
✅ Requisições funcionando  
✅ Login, upload, análises funcionando  
✅ Sem erros de CORS  
✅ Sem erros de conexão  

---

**Pronto!** Seu frontend no Vercel está conectado ao backend no Render! 🚀

