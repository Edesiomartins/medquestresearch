# 🚀 Deploy no Render - MedQuest Research API

## 📋 Pré-requisitos

1. Conta no [Render](https://render.com)
2. Repositório Git (GitHub, GitLab, etc.)
3. Variáveis de ambiente configuradas
4. **IMPORTANTE**: Após o deploy, configure o frontend no Vercel com a URL do Render

## 🔧 Configuração

### 1. Variáveis de Ambiente

#### Backend (Render)

Configure as seguintes variáveis de ambiente no painel do Render:

```bash
# Banco de Dados
DB_HOST=dredesiomartins.mysql.pythonanywhere-services.com
DB_USER=dredesiomartins
DB_PASSWORD=sua_senha
DB_NAME=dredesiomartins$MedquestResearch

# OpenAI
API_OPENAI_KEY_RESEARCH=sk-proj-sua-chave-openai
OPENAI_MODEL=gpt-4o-mini

# API Key
RESEARCH_API_KEY=amordaminhavida162524*

# Flask
FLASK_ENV=production
```

#### Frontend (Vercel)

Após o deploy do backend, configure no Vercel:

```bash
NEXT_PUBLIC_API_BASE_URL=https://seu-app.onrender.com
```

Substitua `seu-app.onrender.com` pela URL real do seu serviço no Render.

📖 **Guia Completo**: Veja `VERCEL_ENV_SETUP.md` para instruções detalhadas.

### 2. Deploy

1. Conecte seu repositório Git ao Render
2. Selecione o serviço `web` configurado no `render.yaml`
3. Render detectará automaticamente o `render.yaml` e configurará o serviço
4. Configure as variáveis de ambiente no painel
5. Clique em "Deploy"

### 3. Build e Start Commands

O Render usará automaticamente:
- **Build**: `pip install -r requirements.txt`
- **Start**: `gunicorn api:app --bind 0.0.0.0:$PORT`

## 📝 Estrutura de Arquivos

```
MedquestResearch/
├── api.py                 # Aplicação Flask principal
├── render.yaml            # Configuração do Render
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
└── README_RENDER.md      # Este arquivo
```

## 🔍 Verificação

Após o deploy, teste a API:

```bash
curl https://seu-app.onrender.com/genapi/health
```

## ⚠️ Notas Importantes

- O Render usa a porta definida pela variável `$PORT` automaticamente
- Certifique-se de que todas as variáveis de ambiente estão configuradas
- O banco de dados MySQL deve estar acessível do Render
- Para produção, considere usar um plano pago para melhor performance

## 🐛 Troubleshooting

### Erro de conexão com banco de dados
- Verifique se o banco permite conexões externas
- Confirme as credenciais nas variáveis de ambiente

### Erro de importação
- Verifique se todas as dependências estão no `requirements.txt`
- Confirme que o Python 3.11 está sendo usado

### Timeout
- Aumente o timeout no painel do Render (Settings > Health Check)

