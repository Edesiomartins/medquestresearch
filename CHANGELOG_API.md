# Changelog - Ajustes da API MedQuestResearch

## 📅 Data: Atualização para API Isolada

### 🎯 Objetivo
Isolar a API do MedQuestResearch do MedQuest Cloud para evitar exposição de chaves sensíveis ao subir para GitHub e Vercel.

## ✅ Alterações Realizadas

### 1. **WSGI.PY** (PythonAnywhere)
- ✅ Adicionado tratamento de erros na importação do `api.py`
- ✅ Adicionado dispatcher condicional com fallback
- ✅ Adicionadas mensagens de debug para troubleshooting
- ✅ Configurado prefixo `/genapi` para isolamento da API Research

### 2. **api.py** (Backend Flask)
- ✅ Corrigido caminho temporário de PDFs (agora usa diretório relativo)
- ✅ Todas as rotas já estão configuradas corretamente

### 3. **gpt_engine.py**
- ✅ Atualizada variável de ambiente: `OPENAI_API_KEY` → `API_OPENAI_KEY_RESEARCH`
- ✅ Mensagem de erro atualizada para mencionar WSGI

### 4. **Frontend (Next.js)**
- ✅ Criado `app/lib/api-config.ts` - Configuração centralizada da API
- ✅ Funções helper para requisições autenticadas
- ✅ Suporte a variáveis de ambiente (`NEXT_PUBLIC_API_URL`)

### 5. **Documentação**
- ✅ Criado `API_CONFIG.md` - Documentação completa da API
- ✅ Atualizado `README.md` com informações de configuração
- ✅ Criado `.gitignore` para proteger arquivos sensíveis

## 🔗 Estrutura de URLs

### Antes
- API misturada com MedQuest Cloud
- Risco de exposição de chaves no Git

### Agora
- **Produção**: `https://dredesiomartins.pythonanywhere.com/genapi`
- **Desenvolvimento**: Configurável via `NEXT_PUBLIC_API_URL`
- **Isolamento**: API Research separada do Cloud

## 🔒 Segurança

### Arquivos Protegidos
- ✅ `WSGI.PY` - Adicionado ao `.gitignore` (contém chaves sensíveis)
- ✅ `.env` - Adicionado ao `.gitignore`
- ✅ Arquivos temporários de PDF

### Variáveis de Ambiente
- **Backend**: Configuradas no `WSGI.PY` (PythonAnywhere)
- **Frontend**: Configuradas no Vercel ou `.env.local`

## 📝 Próximos Passos

1. **Configurar no Vercel**:
   - Adicionar variável `NEXT_PUBLIC_API_URL` no painel do Vercel
   - Valor: `https://dredesiomartins.pythonanywhere.com/genapi`

2. **Usar no Frontend**:
   ```typescript
   import { API_BASE_URL, API_ENDPOINTS, authenticatedFetch } from '@/lib/api-config';
   ```

3. **Testar**:
   - Verificar se as rotas estão acessíveis via `/genapi`
   - Testar autenticação nas rotas Research
   - Verificar rate limiting

## ⚠️ Importante

- **NUNCA** commite o arquivo `WSGI.PY` no Git
- **SEMPRE** use variáveis de ambiente para configurações sensíveis
- **VERIFIQUE** o `.gitignore` antes de fazer commit

