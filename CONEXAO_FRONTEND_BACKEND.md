# 🔗 Conexão Frontend ↔ Backend

## 📋 Resumo

O frontend (Next.js/Vercel) está configurado para se conectar ao backend (Flask) através da variável de ambiente `NEXT_PUBLIC_API_BASE_URL`.

## ⚙️ Como Funciona

### 1. Configuração Atual

O arquivo `app/lib/api-config.ts` gerencia a conexão:

```typescript
// Se NEXT_PUBLIC_API_BASE_URL estiver vazio → usa proxy local
// Se estiver configurado → usa URL direta
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
```

### 2. Configuração

#### Produção e Desenvolvimento
```bash
# .env.local (desenvolvimento) ou Vercel (produção)
NEXT_PUBLIC_API_BASE_URL=https://seu-app.onrender.com
```
- Substitua `seu-app.onrender.com` pela URL real do seu serviço no Render
- Chamadas diretas para o Render
- Funciona tanto em desenvolvimento quanto em produção

## 🚀 Configuração no Vercel

### Passo a Passo

1. **Acesse o Vercel Dashboard**
   - https://vercel.com/dashboard

2. **Selecione o Projeto**
   - Clique em **MedQuestResearch**

3. **Vá em Settings → Environment Variables**

4. **Adicione a Variável**
   - **Key**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: `https://seu-app.onrender.com` (substitua pela URL real do Render)
   - **Environments**: Marque todas (Production, Preview, Development)

5. **Salve e Faça Redeploy**
   - Variáveis só são aplicadas em novos deploys
   - Vá em **Deployments** → **Redeploy**

## ✅ Verificação

Após configurar, teste:

1. **Login**: Deve conectar ao backend
2. **Upload de PDF**: Deve processar corretamente
3. **Análises**: Devem funcionar normalmente

### Debug no Console

Abra o console do navegador (F12) e verifique:
- Requisições devem ir para a URL configurada
- Não deve haver erros de CORS
- Status 200 nas requisições

## 🔍 Troubleshooting

### Erro: "Failed to fetch"
- **Causa**: Backend não está acessível ou CORS não configurado
- **Solução**: Verifique se o backend está rodando e aceita requisições do domínio do Vercel

### Erro: "404 Not Found"
- **Causa**: URL incorreta ou backend não tem a rota `/genapi`
- **Solução**: Verifique a URL e confirme que o backend tem o prefixo `/genapi`

### Erro: "CORS policy"
- **Causa**: Backend não permite requisições do frontend
- **Solução**: Configure CORS no backend para aceitar o domínio do Vercel

### Variável não está sendo aplicada
- **Causa**: Deploy antigo (variáveis só aplicam em novos builds)
- **Solução**: Faça um novo deploy ou redeploy

## 📝 Arquivos Relacionados

- `app/lib/api-config.ts` - Configuração centralizada
- `app/lib/api.ts` - Cliente API
- `next.config.ts` - Configuração do Next.js (proxy)
- `VERCEL_ENV_SETUP.md` - Guia detalhado do Vercel

## 🚀 Setup Inicial

1. **Deploy do Backend no Render**
   - Siga o guia em `DEPLOY_RENDER.md`
   - Anote a URL do serviço (ex: `https://medquest-research-api.onrender.com`)

2. **Configurar Variável no Vercel**
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://medquest-research-api.onrender.com
   ```

3. **Redeploy do Frontend**
   - As requisições irão para o Render

4. **Testar Tudo**
   - Login, upload, análises

## ⚠️ Importante

- **Nunca** commite arquivos `.env` com valores reais
- Use variáveis de ambiente no Vercel para produção
- Para desenvolvimento local, use `.env.local` (já está no `.gitignore`)

