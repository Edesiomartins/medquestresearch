# MedQuestResearch

Plataforma inteligente de leitura crítica, análise científica e geração de conhecimento assistida por IA.

## 🚀 Tecnologias

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Python (processamento de PDFs, análise crítica, fact-checking)

## 📦 Instalação

### Backend (Python)
```bash
pip install -r requirements.txt
```

### Frontend (Next.js)
```bash
npm install
```

## 🛠️ Desenvolvimento

### Executar o servidor de desenvolvimento
```bash
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000) no navegador.

### Build para produção
```bash
npm run build
npm start
```

## 🚀 Deploy no Vercel

O projeto está configurado para deploy automático no Vercel.

### Deploy via Interface Web

1. Acesse [https://vercel.com](https://vercel.com)
2. Faça login com sua conta GitHub
3. Clique em **"Add New Project"**
4. Importe o repositório do GitHub
5. O Vercel detectará automaticamente o Next.js
6. Clique em **"Deploy"**

### Deploy via CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer login
vercel login

# Deploy
vercel
```

## 📁 Estrutura do Projeto

```
MedquestResearch/
├── app/                    # Páginas e componentes Next.js
│   ├── lib/
│   │   └── api-config.ts  # Configuração centralizada da API
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página inicial
│   └── globals.css        # Estilos globais
├── api.py                 # API Python (Flask)
├── database.py            # Configuração do banco de dados
├── pdf_processor.py       # Processamento de PDFs
├── gpt_engine.py          # Engine de IA (OpenAI)
├── requirements.txt       # Dependências Python
├── package.json           # Dependências Node.js
├── API_CONFIG.md          # Documentação da API
└── WSGI.PY                # Configuração PythonAnywhere (não versionado)
```

## ⚙️ Configuração

### Arquivos de Configuração
- `vercel.json` - Configuração do deploy no Vercel
- `API_CONFIG.md` - Documentação completa da API e endpoints
- `app/lib/api-config.ts` - Configuração centralizada da API para o frontend

### Variáveis de Ambiente

#### Frontend (Vercel/Next.js)
Configure no painel do Vercel ou em `.env.local`:
```bash
NEXT_PUBLIC_API_BASE_URL=https://seu-app.onrender.com
```

Substitua `seu-app.onrender.com` pela URL real do seu serviço no Render.

📖 **Guia Completo**: Veja `VERCEL_ENV_SETUP.md` para instruções passo a passo de como adicionar variáveis de ambiente no Vercel.

#### Backend (Render)
As variáveis são configuradas no painel do Render (Environment Variables):
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Configuração do banco de dados
- `API_OPENAI_KEY_RESEARCH` - Chave da API OpenAI
- `RESEARCH_API_KEY` - Chave de autenticação da API Research
- `OPENAI_MODEL` - Modelo GPT (padrão: gpt-4o-mini)
- `FLASK_ENV` - Ambiente Flask (production)

📖 **Guia Completo**: Veja `DEPLOY_RENDER.md` para instruções de deploy no Render.

## 🔄 Deploys Automáticos

Após conectar ao GitHub, cada push para o branch principal fará deploy automático no Vercel.

## 📝 Licença

Este projeto é privado.
