# 🚂 Guia de Deploy no Railway - MedQuestResearch Backend

Este guia explica como fazer deploy do backend do MedQuestResearch no Railway.

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositório no GitHub com o código
3. Chaves de API (Groq e Gemini)

## 🚀 Passo a Passo

### 1. Criar Novo Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositório `medquestresearch`
5. O Railway detectará automaticamente o Python e usará o `nixpacks.toml`

### 2. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

#### Obrigatórias:
```
GROQ_API_KEY=sua-chave-groq-aqui
GEMINI_API_KEY=sua-chave-gemini-aqui
```

#### Banco de Dados (se usar PostgreSQL):
```
DATABASE_URL=postgresql://usuario:senha@host:porta/database
```
*Nota: O Railway pode criar um banco PostgreSQL automaticamente. Use a variável fornecida.*

#### CORS (Frontend):
```
ALLOWED_ORIGINS=https://medquestresearch.vercel.app,https://seu-frontend.vercel.app
```
*Adicione todas as URLs do seu frontend separadas por vírgula*

#### Opcionais:
```
DEBUG=False
LOG_LEVEL=INFO
PORT=8000  # Geralmente não precisa, o Railway define automaticamente
```

### 3. Configurar o Serviço

1. No painel do serviço, vá em **Settings**
2. Verifique o **Root Directory**: Deixe vazio (raiz do projeto)
3. Verifique o **Start Command**: Deve ser `cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT`
   - Isso já está configurado no `nixpacks.toml` e `Procfile`

### 4. Adicionar PostgreSQL (Opcional)

Se precisar de banco de dados:

1. No projeto Railway, clique em **"+ New"**
2. Selecione **"Database"** → **"Add PostgreSQL"**
3. O Railway criará automaticamente e fornecerá a variável `DATABASE_URL`
4. A variável será injetada automaticamente no seu serviço

### 5. Deploy Automático

Após conectar o repositório:
- Cada push para `main` fará deploy automático
- Você pode ver os logs em tempo real no painel
- O Railway fornecerá uma URL pública (ex: `medquest-research-api.up.railway.app`)

### 6. Verificar Deploy

1. Após o deploy, acesse a URL fornecida pelo Railway
2. Teste o endpoint: `https://sua-url.up.railway.app/ping`
3. Deve retornar: `{"status": "Medquestresearch API está ativa ✅", "version": "2.0"}`

## 📁 Arquivos de Configuração

O projeto já inclui:

- ✅ `nixpacks.toml` - Configuração do build (Python 3.12)
- ✅ `Procfile` - Comando de inicialização
- ✅ `railway.json` - Configuração do Railway
- ✅ `runtime.txt` - Versão do Python (3.12)
- ✅ `requirements.txt` - Dependências Python

## 🔧 Troubleshooting

### Erro: "Module not found"
- Verifique se todas as dependências estão no `backend/requirements.txt`
- O Railway instala automaticamente do `requirements.txt` na raiz ou `backend/requirements.txt`

### Erro: "Port already in use"
- O Railway define automaticamente a variável `PORT`
- Não defina `PORT` manualmente, use `$PORT` no comando

### Erro de CORS
- Verifique a variável `ALLOWED_ORIGINS`
- Inclua todas as URLs do frontend (Vercel, etc.)
- Formato: `https://url1.com,https://url2.com` (sem espaços)

### Build falha
- Verifique os logs no Railway
- Certifique-se de que o Python 3.12 está especificado
- Verifique se todas as dependências estão corretas

## 🔗 URLs e Domínios

### Domínio Customizado

1. No painel do serviço, vá em **Settings** → **Domains**
2. Clique em **"Generate Domain"** para obter um domínio `.up.railway.app`
3. Ou adicione um domínio customizado clicando em **"Custom Domain"**

### Atualizar Frontend

Após obter a URL do Railway, atualize o frontend:

1. No Vercel, adicione a variável:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://sua-url.up.railway.app
   ```

2. No backend Railway, adicione a URL do Vercel em `ALLOWED_ORIGINS`

## 📊 Monitoramento

- **Logs**: Veja logs em tempo real no painel do Railway
- **Métricas**: Railway fornece métricas básicas de uso
- **Health Checks**: O endpoint `/ping` pode ser usado para health checks

## 🔄 Deploy Contínuo

O Railway faz deploy automático a cada push para o branch `main`. Para desabilitar:

1. Vá em **Settings** → **Source**
2. Desabilite **"Auto Deploy"**

## 💰 Custos

- Railway oferece um plano gratuito generoso
- Após o limite, você será cobrado por uso
- Consulte [railway.app/pricing](https://railway.app/pricing) para detalhes

## ✅ Checklist Final

- [ ] Projeto criado no Railway
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas (GROQ_API_KEY, GEMINI_API_KEY)
- [ ] ALLOWED_ORIGINS configurado com URLs do frontend
- [ ] Deploy bem-sucedido
- [ ] Endpoint `/ping` funcionando
- [ ] Frontend atualizado com a URL do Railway
- [ ] CORS funcionando corretamente

## 🆘 Suporte

- Documentação Railway: [docs.railway.app](https://docs.railway.app)
- Status: [status.railway.app](https://status.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)
