# Configuração da API - MedQuestResearch

## 📋 Visão Geral

O MedQuestResearch possui uma API própria, acessível através do prefixo `/genapi` no Render.

## 🔗 Estrutura de URLs

### Produção (Render)
- **URL Base**: `https://seu-app.onrender.com/genapi`
- **Configuração**: Definida via variáveis de ambiente no Render

### Desenvolvimento Local
- **URL Base**: Use a mesma URL do Render ou configure via `.env.local`

## 🔐 Variáveis de Ambiente

### Backend (Render)
As seguintes variáveis são configuradas no painel do Render (Environment Variables):

```bash
DB_HOST=dredesiomartins.mysql.pythonanywhere-services.com
DB_USER=dredesiomartins
DB_PASSWORD=sua_senha
DB_NAME=dredesiomartins$MedquestResearch
API_OPENAI_KEY_RESEARCH=sk-proj-sua-chave-openai
OPENAI_MODEL=gpt-4o-mini
RESEARCH_API_KEY=amordaminhavida162524*
FLASK_ENV=production
```

### Frontend (Next.js/Vercel)
Configure no painel do Vercel ou em `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=https://seu-app.onrender.com
```

## 📍 Endpoints Disponíveis

### Rotas Básicas
- `GET /ping` - Verifica se a API está ativa

### Rotas de Usuário
- `POST /cadastro` - Cadastro de novo usuário
- `POST /login` - Login e obtenção de token
- `GET /creditos` - Consulta de créditos (requer autenticação)

### Rotas de IA (Versões Antigas)
- `POST /explicar` - Explicar conceito
- `POST /critica` - Análise crítica
- `POST /fatos` - Verificação de fatos
- `POST /perspectiva` - Pesquisa de perspectivas
- `POST /mapa` - Geração de mapa visual
- `POST /pdf` - Processamento de PDF

### Rotas Research (Novas - Recomendadas)
- `POST /critical_analysis` - Análise crítica (requer `@require_api_key`)
- `POST /explain_concept` - Explicar conceito (requer `@require_api_key`)
- `POST /fact_checker` - Verificação de fatos (requer `@require_api_key`)
- `POST /perspective_research` - Pesquisa de perspectivas (requer `@require_api_key`)

## 🔒 Autenticação

### Rotas com `@require_api_key`
As rotas Research requerem autenticação via header:

```typescript
headers: {
  'Authorization': `Bearer ${token}`
}
```

### Rate Limiting
Todas as rotas sensíveis possuem rate limiting:
- **Limite padrão**: 100 requisições/dia, 10/minuto
- **Limite por rota**: 5 requisições/minuto

## 💻 Uso no Frontend

### Importar configuração
```typescript
import { API_BASE_URL, API_ENDPOINTS, authenticatedFetch } from '@/lib/api-config';
```

### Exemplo de chamada
```typescript
const response = await authenticatedFetch(
  API_ENDPOINTS.CRITICAL_ANALYSIS,
  {
    method: 'POST',
    body: JSON.stringify({
      texto_artigo: '...'
    })
  },
  token // token do usuário autenticado
);

const data = await response.json();
```

## 🚨 Segurança

### ⚠️ IMPORTANTE
- **NUNCA** commite o arquivo `WSGI.PY` no Git (já está no `.gitignore`)
- **NUNCA** commite arquivos `.env` com chaves reais
- Use variáveis de ambiente no Vercel para configurações sensíveis
- As chaves de API ficam apenas no PythonAnywhere (WSGI.PY)

## 📝 Notas de Deploy

1. **Render**: Configure todas as variáveis de ambiente no painel do Render
2. **Vercel**: Configure `NEXT_PUBLIC_API_BASE_URL` com a URL do Render
3. **GitHub**: O código não contém chaves sensíveis (protegido pelo `.gitignore`)

