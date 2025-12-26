# Frontend - MedQuest Research

Frontend Next.js para o MedQuestResearch.

## 📁 Estrutura

```
frontend/
├── app/                  # Páginas e componentes Next.js
│   ├── (auth)/          # Páginas de autenticação
│   ├── components/      # Componentes React
│   ├── lib/            # Utilitários e hooks
│   └── ...
├── public/              # Arquivos estáticos
├── package.json        # Dependências Node.js
├── next.config.ts      # Configuração do Next.js
└── ...
```

## 🚀 Instalação

```bash
npm install
```

## 🛠️ Desenvolvimento

```bash
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000)

## 🚀 Deploy no Vercel

1. Configure a variável de ambiente `NEXT_PUBLIC_API_BASE_URL` com a URL do backend no Render
2. Siga o guia em `VERCEL_ENV_SETUP.md`

## ⚙️ Variáveis de Ambiente

Configure no Vercel:
- `NEXT_PUBLIC_API_BASE_URL` - URL do backend no Render (ex: `https://seu-app.onrender.com`)

## 📝 Documentação

- `VERCEL_ENV_SETUP.md` - Guia de configuração no Vercel
- `../CONEXAO_FRONTEND_BACKEND.md` - Como conectar frontend e backend

