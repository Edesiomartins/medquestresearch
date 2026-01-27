# 🔑 Configurar Chaves de API

## ❌ Erro: API_OPENAI_KEY_RESEARCH não configurada

Este erro significa que a chave da API não está configurada no arquivo `.env`.

## ✅ Solução: Adicionar Chave de API

### Opção 1: Obter do Railway (Recomendado)

1. Acesse: https://railway.app
2. Selecione seu projeto **MedquestResearch**
3. Vá em **Variables** (ou **Settings** → **Variables**)
4. Procure por `API_OPENAI_KEY_RESEARCH`
5. Copie o valor

### Opção 2: Criar Nova Chave

**Se usar OpenRouter:**
1. Acesse: https://openrouter.ai/keys
2. Faça login ou crie uma conta
3. Crie uma nova chave de API
4. Copie a chave

**Se usar OpenAI diretamente:**
1. Acesse: https://platform.openai.com/api-keys
2. Faça login
3. Crie uma nova chave de API
4. Copie a chave

### Configurar no .env

Abra o arquivo `backend/.env` e adicione:

```env
# Chave da API (OBRIGATÓRIA)
API_OPENAI_KEY_RESEARCH=sua_chave_aqui

# Se usar OpenRouter, também adicione:
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

**Exemplo completo:**

```env
DATABASE_URL=postgresql://postgres:senha@host:porta/database?sslmode=require

# Chave OpenRouter
API_OPENAI_KEY_RESEARCH=sk-or-v1-abc123def456...
OPENAI_API_BASE=https://openrouter.ai/api/v1

# Modelo (opcional)
OPENAI_MODEL=gpt-5-mini
```

### Reiniciar o Backend

Depois de adicionar a chave:

1. Pare o backend (Ctrl+C)
2. Inicie novamente:
   ```powershell
   cd backend
   python api.py
   ```

### Verificar se Funcionou

Teste a metanálise novamente. Se ainda der erro, verifique:

1. A chave está correta (sem espaços extras)
2. O arquivo `.env` está em `backend/.env`
3. O backend foi reiniciado após adicionar a chave
4. A chave tem créditos disponíveis (se OpenRouter)

## 🔒 Segurança

- **NÃO commite o arquivo `.env` no Git**
- **NÃO compartilhe sua chave publicamente**
- **Use variáveis de ambiente no Railway para produção**

## 📝 Variáveis Disponíveis

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `API_OPENAI_KEY_RESEARCH` | ✅ Sim | Chave da API OpenAI/OpenRouter |
| `OPENAI_API_BASE` | ⚠️ Se OpenRouter | Base URL (https://openrouter.ai/api/v1) |
| `OPENAI_MODEL` | ❌ Não | Modelo a usar (padrão: gpt-5-mini) |
| `OPENROUTER_MAX_OUTPUT_TOKENS` | ❌ Não | Máx tokens (padrão: 4000) |
