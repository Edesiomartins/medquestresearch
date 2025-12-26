# 🚀 Guia de Deploy no Render - MedQuest Research API

## ✅ Arquivos Preparados

Os seguintes arquivos foram criados/atualizados para deploy no Render:

### 📄 Arquivos Criados

1. **`render.yaml`** - Configuração do serviço web no Render
2. **`.env.example`** - Template de variáveis de ambiente
3. **`README_RENDER.md`** - Documentação completa do deploy
4. **`DEPLOY_RENDER.md`** - Este guia rápido

### 🔧 Arquivos Atualizados

1. **`requirements.txt`** - Adicionado `gunicorn` para produção
2. **`database.py`** - Modificado para usar variáveis de ambiente
3. **`api.py`** - Adicionado suporte para execução local com `if __name__ == "__main__"`
4. **`.gitignore`** - Adicionado `wsgi.py` para não expor chaves

## 📋 Passos para Deploy

### 1. Preparar Repositório

```bash
# Verificar se todos os arquivos estão commitados
git status

# Adicionar arquivos novos
git add render.yaml .env.example README_RENDER.md DEPLOY_RENDER.md
git add requirements.txt database.py api.py .gitignore

# Commit
git commit -m "Preparar para deploy no Render"

# Push
git push origin main
```

### 2. Configurar no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** > **"Web Service"**
3. Conecte seu repositório Git
4. Render detectará automaticamente o `render.yaml`

### 3. Configurar Variáveis de Ambiente

#### Backend (Render)

No painel do Render, vá em **Environment** e adicione:

```bash
DB_HOST=dredesiomartins.mysql.pythonanywhere-services.com
DB_USER=dredesiomartins
DB_PASSWORD=sua_senha_aqui
DB_NAME=dredesiomartins$MedquestResearch
API_OPENAI_KEY_RESEARCH=sk-proj-sua-chave-openai
OPENAI_MODEL=gpt-4o-mini
RESEARCH_API_KEY=amordaminhavida162524*
FLASK_ENV=production
```

#### Frontend (Vercel)

Após o deploy do backend no Render, configure no Vercel:

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Vá em **Settings** → **Environment Variables**
3. Adicione:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://seu-app.onrender.com
   ```
4. Substitua `seu-app.onrender.com` pela URL real do seu serviço no Render
5. Faça um novo deploy no Vercel

📖 **Guia Completo**: Veja `VERCEL_ENV_SETUP.md` para instruções detalhadas.

### 4. Deploy

1. Clique em **"Create Web Service"**
2. Render iniciará o build automaticamente
3. Aguarde o deploy completar (pode levar alguns minutos)

### 5. Verificar

Após o deploy, teste a API:

```bash
# Health check
curl https://seu-app.onrender.com/genapi/health

# Deve retornar: {"status": "ok"}
```

## 🔍 Estrutura de Rotas

A API estará disponível em:
- `https://seu-app.onrender.com/genapi/health` - Health check
- `https://seu-app.onrender.com/genapi/login` - Login
- `https://seu-app.onrender.com/genapi/critica` - Análise crítica
- `https://seu-app.onrender.com/genapi/pdf` - Upload de PDF
- E outras rotas conforme `api.py`

## ⚠️ Importante

1. **Banco de Dados**: Certifique-se de que o MySQL permite conexões externas do Render
2. **Timeout**: O plano free tem timeout de 30s. Considere upgrade para requisições longas
3. **Sleep**: O plano free "dorme" após inatividade. Primeira requisição pode demorar
4. **Variáveis**: Nunca commite arquivos `.env` ou `wsgi.py` com chaves reais

## 🐛 Troubleshooting

### Erro: "Cannot connect to database"
- Verifique se o banco permite conexões externas
- Confirme credenciais nas variáveis de ambiente

### Erro: "Module not found"
- Verifique se todas as dependências estão no `requirements.txt`
- Confirme que o build completou sem erros

### Timeout
- Aumente o timeout em Settings > Health Check
- Considere usar jobs assíncronos para tarefas longas

### App "dormindo"
- No plano free, o app dorme após 15min de inatividade
- Primeira requisição após dormir pode levar ~30s
- Upgrade para plano pago para evitar isso

## 📞 Suporte

- Documentação Render: https://render.com/docs
- Logs: Acesse via Dashboard > Logs
- Status: Verifique em Dashboard > Events

