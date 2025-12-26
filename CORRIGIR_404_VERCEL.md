# 🔧 Corrigir Erro 404 no Vercel

## ❌ Problema

```
404: NOT_FOUND Code: NOT_FOUND ID: gru1:gru1::72b7d-1766778403118-82626a7cc6e5
```

O Vercel não está encontrando os arquivos do Next.js porque o frontend está na pasta `frontend/`, mas o Vercel está procurando na raiz.

## ✅ Solução: Configurar Root Directory no Vercel

### Passo 1: Acessar Configurações do Projeto

1. Acesse: https://vercel.com/dashboard
2. Selecione seu projeto **MedQuestResearch**
3. Vá em **Settings** → **General**

### Passo 2: Configurar Root Directory

1. Role até a seção **Root Directory**
2. Clique em **Edit**
3. Digite: `frontend`
4. Clique em **Save**

### Passo 3: Verificar Build Settings

Certifique-se de que as configurações estão assim:

**Build & Development Settings:**
- **Framework Preset**: `Next.js` (deve detectar automaticamente)
- **Root Directory**: `frontend` ✅
- **Build Command**: Deixe vazio (auto-detecta `npm run build`)
- **Output Directory**: Deixe vazio (auto-detecta `.next`)
- **Install Command**: Deixe vazio (auto-detecta `npm install`)

### Passo 4: Fazer Novo Deploy

1. Vá em **Deployments**
2. Clique nos **três pontos (⋯)** do último deploy
3. Selecione **Redeploy**
4. Aguarde o deploy completar

## 🔍 Verificação

Após o deploy:

1. Acesse sua aplicação no Vercel
2. Deve carregar normalmente (sem erro 404)
3. Teste fazer login ou navegar pelas páginas

## 📋 Estrutura do Projeto

O projeto está organizado assim:

```
MedquestResearch/              ← Raiz do repositório Git
├── frontend/                   ← Frontend Next.js (Root Directory no Vercel)
│   ├── app/
│   ├── package.json
│   ├── next.config.ts
│   └── ...
├── backend/                    ← Backend Python (deploy no Render)
│   ├── api.py
│   └── ...
└── render.yaml                 ← Configuração do Render
```

## ⚠️ Importante

- **Root Directory no Vercel**: `frontend`
- **Root Directory no Render**: `backend` (já configurado no `render.yaml`)

## 🔄 Se Ainda Não Funcionar

1. **Limpe o cache do build**:
   - Vá em **Deployments** → **Redeploy**
   - **Desmarque** "Use existing Build Cache"
   - Clique em **Redeploy**

2. **Verifique os logs do build**:
   - Vá em **Deployments** → Clique no deploy
   - Veja os logs completos
   - Procure por erros de build

3. **Verifique se os arquivos estão no Git**:
   ```bash
   git ls-files frontend/
   ```
   Todos os arquivos do frontend devem estar commitados.

---

**Após configurar o Root Directory como `frontend`, o erro 404 deve desaparecer!** ✅

