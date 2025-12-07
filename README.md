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
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página inicial
│   └── globals.css        # Estilos globais
├── api.py                 # API Python
├── database.py            # Configuração do banco de dados
├── pdf_processor.py       # Processamento de PDFs
├── gpt_engine.py          # Engine de IA
├── requirements.txt       # Dependências Python
└── package.json           # Dependências Node.js
```

## ⚙️ Configuração

O arquivo `vercel.json` está configurado para:
- Framework: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`

## 🔄 Deploys Automáticos

Após conectar ao GitHub, cada push para o branch principal fará deploy automático no Vercel.

## 📝 Licença

Este projeto é privado.
