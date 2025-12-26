# MedQuestResearch

Plataforma inteligente de leitura crítica, análise científica e geração de conhecimento assistida por IA.

## 📁 Estrutura do Projeto

```
MedquestResearch/
├── backend/              # Backend Python (Flask)
│   ├── api.py           # Aplicação Flask principal
│   ├── database.py      # Configuração do banco de dados
│   ├── gpt_engine.py    # Engine de IA (OpenAI)
│   ├── requirements.txt # Dependências Python
│   ├── render.yaml      # Configuração do Render
│   └── ...              # Outros módulos Python
│
├── frontend/            # Frontend Next.js
│   ├── app/            # Páginas e componentes Next.js
│   ├── package.json    # Dependências Node.js
│   ├── next.config.ts  # Configuração do Next.js
│   └── ...             # Outros arquivos do frontend
│
└── README.md           # Este arquivo
```

## 🚀 Tecnologias

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Python (Flask), OpenAI API, PyMuPDF

## 📦 Instalação

### Backend (Python)

```bash
cd backend
pip install -r requirements.txt
```

### Frontend (Next.js)

```bash
cd frontend
npm install
```

## 🛠️ Desenvolvimento

### Backend

```bash
cd backend
python api.py
```

O servidor Flask estará disponível em `http://localhost:5000`

### Frontend

```bash
cd frontend
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000) no navegador.

## 🚀 Deploy

### Backend (Render)

Siga o guia em `backend/README_RENDER.md` ou `backend/DEPLOY_RENDER.md`

### Frontend (Vercel)

1. Configure a variável de ambiente `NEXT_PUBLIC_API_BASE_URL` com a URL do Render
2. Siga o guia em `frontend/VERCEL_ENV_SETUP.md`

## ⚙️ Configuração

### Variáveis de Ambiente

#### Backend (Render)
Configure no painel do Render:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `API_OPENAI_KEY_RESEARCH`
- `RESEARCH_API_KEY`
- `OPENAI_MODEL`
- `FLASK_ENV`

#### Frontend (Vercel)
Configure no painel do Vercel:
- `NEXT_PUBLIC_API_BASE_URL` - URL do backend no Render

📖 **Guias Completos**:
- Backend: `backend/DEPLOY_RENDER.md`
- Frontend: `frontend/VERCEL_ENV_SETUP.md`
- Conexão: `CONEXAO_FRONTEND_BACKEND.md`

## 📝 Documentação

- `backend/API_CONFIG.md` - Documentação da API
- `backend/README_RENDER.md` - Deploy no Render
- `frontend/VERCEL_ENV_SETUP.md` - Configuração do Vercel
- `CONEXAO_FRONTEND_BACKEND.md` - Como conectar frontend e backend

## 📝 Licença

Este projeto é privado.
