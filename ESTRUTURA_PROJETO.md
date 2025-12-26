# 📁 Estrutura do Projeto MedQuestResearch

## Organização

O projeto foi reorganizado em duas pastas principais:

```
MedquestResearch/
├── backend/              # Backend Python (Flask)
│   ├── api.py           # Aplicação Flask principal
│   ├── database.py      # Configuração do banco de dados
│   ├── gpt_engine.py    # Engine de IA (OpenAI)
│   ├── pdf_processor.py # Processamento de PDFs
│   ├── requirements.txt # Dependências Python
│   └── ...              # Outros módulos Python
│
├── frontend/            # Frontend Next.js
│   ├── app/            # Páginas e componentes Next.js
│   ├── package.json    # Dependências Node.js
│   ├── next.config.ts  # Configuração do Next.js
│   └── ...             # Outros arquivos do frontend
│
├── render.yaml          # Configuração do Render (backend)
├── README.md           # Documentação principal
└── ...                  # Outros arquivos de documentação
```

## 🚀 Comandos

### Backend

```bash
# Instalar dependências
cd backend
pip install -r requirements.txt

# Executar localmente
python api.py
```

### Frontend

```bash
# Instalar dependências
cd frontend
npm install

# Executar localmente
npm run dev
```

## 📝 Documentação

- **Raiz**: `README.md` - Visão geral do projeto
- **Backend**: `backend/README.md` - Documentação do backend
- **Frontend**: `frontend/README.md` - Documentação do frontend
- **Deploy**: `DEPLOY_RENDER.md` - Guia de deploy no Render
- **Conexão**: `CONEXAO_FRONTEND_BACKEND.md` - Como conectar frontend e backend

## ⚙️ Configuração

### Backend (Render)
- Configure variáveis de ambiente no painel do Render
- Veja `DEPLOY_RENDER.md` para detalhes

### Frontend (Vercel)
- Configure `NEXT_PUBLIC_API_BASE_URL` no Vercel
- Veja `VERCEL_ENV_SETUP.md` para detalhes

