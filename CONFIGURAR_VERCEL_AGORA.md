# ⚡ Configurar Vercel AGORA - URL Real

## 🎯 URL do Backend

**Backend Render**: `https://medquestresearch.onrender.com`

✅ API está funcionando! Teste: https://medquestresearch.onrender.com

## 🚀 Configuração no Vercel (3 Passos Simples)

### Passo 1: Acessar o Vercel

1. Acesse: https://vercel.com/dashboard
2. Selecione seu projeto **MedQuestResearch**

### Passo 2: Configurar Variável de Ambiente

1. Vá em **Settings** → **Environment Variables**
2. Procure por `NEXT_PUBLIC_API_BASE_URL`
   - Se **existir**: Clique em **Edit** (ícone de lápis)
   - Se **não existir**: Clique em **Add New**
3. Configure exatamente assim:
   - **Key**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: `https://medquestresearch.onrender.com`
   - **Environments**: Marque TODAS as opções:
     - ✅ Production
     - ✅ Preview
     - ✅ Development
4. Clique em **Save**

### Passo 3: Fazer Redeploy (OBRIGATÓRIO!)

⚠️ **CRÍTICO**: Variáveis de ambiente só são aplicadas em novos deploys!

1. Vá em **Deployments** (menu lateral)
2. Clique nos **três pontos (⋯)** do último deploy
3. Selecione **Redeploy**
4. Aguarde 2-5 minutos para o deploy completar

## ✅ Como Verificar se Funcionou

Após o deploy:

1. **Acesse sua aplicação no Vercel**
   - URL estará em **Deployments** → **Domains**

2. **Abra o Console do Navegador (F12)**
   - Vá na aba **Network** (Rede)

3. **Teste fazer Login ou Upload de PDF**
   - As requisições devem aparecer indo para:
     - `https://medquestresearch.onrender.com/genapi/login`
     - `https://medquestresearch.onrender.com/genapi/pdf`
   - Status deve ser **200** (sucesso)
   - **NÃO** deve aparecer erro de CORS

## 📋 Resumo da Configuração

```
Variável: NEXT_PUBLIC_API_BASE_URL
Valor: https://medquestresearch.onrender.com
```

**Como funciona:**
- Frontend usa: `NEXT_PUBLIC_API_BASE_URL` = `https://medquestresearch.onrender.com`
- Código adiciona `/genapi` automaticamente
- Resultado final: `https://medquestresearch.onrender.com/genapi/login`

## 🔍 Troubleshooting

### ❌ Erro: "NEXT_PUBLIC_API_BASE_URL não configurado"

**Solução**:
1. Verifique se a variável está salva no Vercel
2. **Faça um REDEPLOY** (variáveis só aplicam em novos builds)

### ❌ Erro: "CORS policy blocked"

**Solução**: 
- O CORS já está configurado no backend
- Se persistir, verifique se o backend está rodando no Render

### ❌ Erro: "404 Not Found"

**Solução**:
1. Verifique se a URL está correta (sem barra no final)
2. Teste diretamente: `https://medquestresearch.onrender.com`
3. Deve retornar JSON com status

### ❌ Requisições ainda não funcionam

**Solução**:
1. Limpe o cache do navegador (Ctrl+Shift+R)
2. Teste em aba anônima
3. Verifique os logs do Vercel (Deployments → Logs)
4. Verifique os logs do Render (para ver se as requisições estão chegando)

## 📝 Checklist Final

- [ ] Variável `NEXT_PUBLIC_API_BASE_URL` configurada no Vercel
- [ ] Valor: `https://medquestresearch.onrender.com` (sem barra no final)
- [ ] Aplicada a todas as environments (Production, Preview, Development)
- [ ] Redeploy feito no Vercel
- [ ] Testado login/upload e funcionando
- [ ] Sem erros no console do navegador

---

**Pronto!** Siga os 3 passos acima e seu frontend estará conectado ao backend! 🚀

**URL do Backend**: https://medquestresearch.onrender.com
