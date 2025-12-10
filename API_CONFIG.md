# Configuração da API - MedQuestResearch

## 📋 Visão Geral

O MedQuestResearch possui uma API própria isolada do MedQuest Cloud, acessível através do prefixo `/genapi` no PythonAnywhere.

## 🔗 Estrutura de URLs

### Produção (PythonAnywhere)
- **URL Base**: `https://dredesiomartins.pythonanywhere.com/genapi`
- **Configuração**: Definida no arquivo `WSGI.PY` (não versionado no Git)

### Desenvolvimento Local
- **URL Base**: `https://dredesiomartins.pythonanywhere.com/genapi` (ou configure localhost se necessário)

## 🔐 Variáveis de Ambiente

### Backend (PythonAnywhere - WSGI.PY)
As seguintes variáveis são configuradas no `WSGI.PY`:

```python
os.environ["API_OPENAI_KEY_RESEARCH"] = "sua-chave-openai"
os.environ["RESEARCH_API_KEY"] = "sua-chave-research"
```

### Frontend (Next.js/Vercel)
Configure no painel do Vercel ou em `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://dredesiomartins.pythonanywhere.com/genapi
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

1. **PythonAnywhere**: O `WSGI.PY` configura as variáveis de ambiente e monta o dispatcher
2. **Vercel**: Configure `NEXT_PUBLIC_API_URL` nas variáveis de ambiente
3. **GitHub**: O código não contém chaves sensíveis (protegido pelo `.gitignore`)

