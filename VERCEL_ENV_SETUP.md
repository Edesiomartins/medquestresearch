# 🔧 Configuração de Variáveis de Ambiente no Vercel

## 📋 Variáveis Necessárias

Configure a seguinte variável de ambiente no Vercel:

### `NEXT_PUBLIC_API_BASE_URL`

**Descrição**: URL base do backend da API MedQuestResearch

**Valor**:

```
https://seu-app.onrender.com
```

Substitua `seu-app.onrender.com` pela URL real do seu serviço no Render.

## 🚀 Como Configurar no Vercel

### Método 1: Via Dashboard Web

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Selecione seu projeto **MedQuestResearch**
3. Vá em **Settings** → **Environment Variables**
4. Clique em **Add New**
5. Configure:
   - **Key**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: `https://seu-app.onrender.com` (substitua pela URL real do Render)
   - **Environments**: Selecione `Production`, `Preview` e `Development`
6. Clique em **Save**
7. **Importante**: Faça um novo deploy para aplicar as mudanças

### Método 2: Via CLI

```bash
# Instalar Vercel CLI (se ainda não tiver)
npm i -g vercel

# Fazer login
vercel login

# Adicionar variável de ambiente
vercel env add NEXT_PUBLIC_API_BASE_URL

# Quando solicitado, digite o valor:
# https://dredesiomartins.pythonanywhere.com

# Aplicar a todas as environments
vercel env pull .env.local
```

## 🔄 Após Configurar

1. **Redeploy obrigatório**: As variáveis de ambiente só são aplicadas em novos deploys
2. Vá em **Deployments** → Selecione o último deploy → **Redeploy**
3. Ou faça um novo commit e push para trigger automático

## ✅ Verificação

Após o deploy, verifique se está funcionando:

1. Acesse sua aplicação no Vercel
2. Abra o console do navegador (F12)
3. Verifique se as requisições estão indo para a URL correta
4. Teste fazer login ou upload de PDF

## 🔍 Troubleshooting

### Problema: Requisições ainda vão para URL antiga

**Solução**: 
- Verifique se a variável está configurada corretamente
- Faça um novo deploy (as variáveis só são aplicadas em novos builds)
- Limpe o cache do navegador

### Problema: CORS errors

**Solução**:
- Verifique se o backend está configurado para aceitar requisições do domínio do Vercel
- Confirme que o CORS está habilitado no backend

### Problema: 404 Not Found

**Solução**:
- Verifique se a URL está correta (sem barra no final)
- Confirme que o backend está rodando e acessível
- Teste a URL diretamente no navegador: `https://sua-url.com/genapi/health`

## 📝 Notas

- Variáveis que começam com `NEXT_PUBLIC_` são expostas ao cliente (browser)
- Não coloque chaves secretas em variáveis `NEXT_PUBLIC_*`
- Para desenvolvimento local, crie um arquivo `.env.local` com as mesmas variáveis
