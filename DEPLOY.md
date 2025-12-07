# Instruções de Deploy no Vercel

## ✅ O que já está configurado:
- ✅ Repositório Git inicializado
- ✅ Commits realizados
- ✅ `vercel.json` configurado na raiz
- ✅ `.gitignore` criado
- ✅ README.md criado

## 📤 Passo 1: Push para o GitHub

Se ainda não fez o push dos commits mais recentes:

```bash
git push origin master
```

Ou se o branch principal for `main`:
```bash
git branch -M main
git push origin main
```

## 🚀 Passo 2: Deploy no Vercel

### Opção A: Via Interface Web (Recomendado)

1. Acesse: https://vercel.com
2. Faça login com sua conta GitHub
3. Clique em **"Add New Project"**
4. Selecione o repositório **MedquestResearch**
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `medquestgen-frontend`
   - **Build Command**: `npm run build` (automático)
   - **Output Directory**: `.next` (automático)
6. Clique em **"Deploy"**

### Opção B: Via CLI do Vercel

```bash
# Instalar Vercel CLI globalmente
npm i -g vercel

# Fazer login
vercel login

# Deploy (no diretório do projeto)
cd medquestgen-frontend
vercel

# Ou fazer deploy a partir da raiz especificando o diretório
vercel --cwd medquestgen-frontend
```

## ⚙️ Configuração Importante

O arquivo `vercel.json` na raiz já está configurado com:
- **rootDirectory**: `medquestgen-frontend`
- **framework**: `nextjs`
- **buildCommand**: `npm install && npm run build`
- **outputDirectory**: `.next`

O Vercel detectará automaticamente essas configurações!

## 🔄 Deploys Automáticos

Após conectar ao GitHub, cada push para o branch principal (`master` ou `main`) fará deploy automático no Vercel.

## 🌍 Variáveis de Ambiente

Se seu projeto precisar de variáveis de ambiente:
1. Vá em **Settings** → **Environment Variables** no painel do Vercel
2. Adicione as variáveis necessárias
3. Os valores estarão disponíveis em `process.env.NOME_DA_VARIAVEL`

## 📝 Próximos Passos

Após o primeiro deploy:
- O Vercel gerará uma URL pública (ex: `medquestresearch.vercel.app`)
- Você pode adicionar um domínio customizado em **Settings** → **Domains**
- Cada commit será automaticamente deployado

## ❓ Problemas Comuns

### Build falha?
- Verifique se todas as dependências estão no `package.json`
- Confirme que o `Root Directory` está como `medquestgen-frontend`

### Erro de módulo não encontrado?
- Verifique se o `package.json` está completo
- Execute `npm install` localmente para testar

### Deploy não atualiza?
- Verifique se o push foi feito para o branch correto
- Veja os logs no painel do Vercel
