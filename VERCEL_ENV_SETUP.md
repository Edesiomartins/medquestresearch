# 🔧 Como Adicionar Variáveis de Ambiente no Vercel

## 📍 Passo a Passo Detalhado

### 1️⃣ Acesse o Painel do Vercel

1. Acesse: **https://vercel.com**
2. Faça login com sua conta (GitHub, GitLab ou Bitbucket)

### 2️⃣ Selecione seu Projeto

1. No **Dashboard**, encontre o projeto **MedquestResearch**
2. Clique no nome do projeto para abrir

### 3️⃣ Acesse as Configurações

1. No menu superior do projeto, clique em **"Settings"** (Configurações)
2. No menu lateral esquerdo, clique em **"Environment Variables"** (Variáveis de Ambiente)

### 4️⃣ Adicione a Variável

1. Você verá uma seção com campos para adicionar variáveis
2. Preencha os campos:

   **Key (Chave):** ⚠️ **COPIE EXATAMENTE** (sem espaços extras)
   ```
   NEXT_PUBLIC_API_URL
   ```
   
   ⚠️ **IMPORTANTE**: 
   - Use apenas letras MAIÚSCULAS
   - Use underscores (_) para separar palavras
   - NÃO use hífens (-), pontos (.) ou espaços
   - NÃO comece com número
   - Exemplo correto: `NEXT_PUBLIC_API_URL`
   - Exemplo ERRADO: `NEXT-PUBLIC-API-URL` ou `next_public_api_url`

   **Value (Valor):**
   ```
   https://dredesiomartins.pythonanywhere.com/genapi
   ```

3. Selecione os **Environments** (Ambientes) onde a variável será usada:
   - ✅ **Production** (Produção)
   - ✅ **Preview** (Preview/Staging)
   - ✅ **Development** (Desenvolvimento) - opcional

4. Clique no botão **"Add"** ou **"Save"**

### 5️⃣ Verificar se foi Adicionada

Após adicionar, você verá a variável listada na tabela:
- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://dredesiomartins.pythonanywhere.com/genapi` (oculto por segurança)
- **Environments**: Production, Preview, Development

### 6️⃣ Fazer Novo Deploy (Importante!)

⚠️ **IMPORTANTE**: Após adicionar variáveis de ambiente, você precisa fazer um novo deploy:

**Opção A - Deploy Automático:**
- Faça um commit e push para o GitHub
- O Vercel detectará automaticamente e fará deploy com as novas variáveis

**Opção B - Redeploy Manual:**
1. Vá para a aba **"Deployments"** (Deploys)
2. Clique nos três pontos (⋯) do último deploy
3. Selecione **"Redeploy"**
4. Confirme o redeploy

## 📸 Visualização da Interface

```
Vercel Dashboard
└── MedquestResearch (projeto)
    └── Settings
        └── Environment Variables
            └── [Formulário]
                ├── Key: NEXT_PUBLIC_API_URL
                ├── Value: https://dredesiomartins.pythonanywhere.com/genapi
                ├── ☑ Production
                ├── ☑ Preview
                └── ☐ Development (opcional)
                └── [Add/Save Button]
```

## ✅ Verificação

Para verificar se a variável está funcionando:

1. Após o deploy, acesse sua aplicação no Vercel
2. Abra o **Console do Navegador** (F12 → Console)
3. Execute no console:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL);
   ```
4. Deve retornar: `https://dredesiomartins.pythonanywhere.com/genapi`

## 🔍 Alternativa: Via CLI do Vercel

Se preferir usar a linha de comando:

```bash
# Instalar Vercel CLI (se ainda não tiver)
npm i -g vercel

# Fazer login
vercel login

# Adicionar variável de ambiente
vercel env add NEXT_PUBLIC_API_URL

# Quando solicitado, digite o valor:
# https://dredesiomartins.pythonanywhere.com/genapi

# Selecione os ambientes (Production, Preview, Development)
```

## ⚠️ Observações Importantes

1. **Prefixo `NEXT_PUBLIC_`**: 
   - Variáveis que começam com `NEXT_PUBLIC_` são expostas ao cliente (browser)
   - Use apenas para valores que podem ser públicos
   - NUNCA use para chaves secretas!

2. **Redeploy Necessário**:
   - Variáveis de ambiente são injetadas no momento do build
   - Sempre faça um novo deploy após adicionar/modificar variáveis

3. **Valores Sensíveis**:
   - Se precisar de valores secretos, use variáveis SEM o prefixo `NEXT_PUBLIC_`
   - Essas variáveis só estarão disponíveis no servidor (API Routes)

## 🆘 Problemas Comuns

### ❌ Erro: "The name contains invalid characters"
**Causa**: O nome da variável contém caracteres inválidos.

**Solução**:
- ✅ Use APENAS letras MAIÚSCULAS (A-Z)
- ✅ Use underscores (_) para separar palavras
- ✅ NÃO use: hífens (-), pontos (.), espaços, ou outros caracteres especiais
- ✅ NÃO comece com número
- ✅ Nome correto: `NEXT_PUBLIC_API_URL`
- ✅ Nomes ERRADOS: `NEXT-PUBLIC-API-URL`, `next_public_api_url`, `NEXT.PUBLIC.API.URL`

**Exemplo de nomes válidos**:
- ✅ `NEXT_PUBLIC_API_URL`
- ✅ `API_BASE_URL`
- ✅ `MY_VARIABLE_NAME`

**Exemplo de nomes inválidos**:
- ❌ `NEXT-PUBLIC-API-URL` (hífen não permitido)
- ❌ `next_public_api_url` (minúsculas podem causar problemas)
- ❌ `NEXT.PUBLIC.API.URL` (ponto não permitido)
- ❌ `123_API_URL` (não pode começar com número)

### Variável não aparece no código?
- ✅ Verifique se fez redeploy após adicionar
- ✅ Verifique se o nome está correto: `NEXT_PUBLIC_API_URL` (copie exatamente)
- ✅ Verifique se selecionou o ambiente correto (Production)

### Erro 404 nas chamadas de API?
- ✅ Verifique se a URL está correta: `https://dredesiomartins.pythonanywhere.com/genapi`
- ✅ Verifique se o prefixo `/genapi` está configurado no WSGI.PY
- ✅ Teste a URL diretamente no navegador: `https://dredesiomartins.pythonanywhere.com/genapi/ping`

### Como editar uma variável existente?
1. Vá em **Settings** → **Environment Variables**
2. Clique nos três pontos (⋯) ao lado da variável
3. Selecione **"Edit"**
4. Modifique o valor
5. Salve e faça redeploy

## 📚 Documentação Oficial

Para mais informações, consulte:
- https://vercel.com/docs/concepts/projects/environment-variables

