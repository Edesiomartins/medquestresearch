# Variáveis de ambiente no Railway

## Serviço Backend (API)

No painel do Railway, no **serviço do backend** (API), em **Variables** (Variáveis), configure:

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | URL de conexão PostgreSQL. Use o **vínculo com o Postgres** do Railway (veja seção abaixo) ou cole a URL manualmente. | `postgresql://usuario:senha@host:porta/nome_do_banco` |
| `API_OPENAI_KEY_RESEARCH` | Chave da API de IA. Pode ser: **OpenAI** ([platform.openai.com](https://platform.openai.com/api-keys)) ou **OpenRouter** ([openrouter.ai](https://openrouter.ai/keys)) — se usar OpenRouter, defina também `OPENAI_API_BASE`. | `sk-proj-...` ou `sk-or-v1-...` |

### Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OPENAI_MODEL` | Modelo de IA. **Padrão:** `gpt-5-mini` (mais capaz, versão econômica do GPT-5). Alternativas: `gpt-4o-mini` (por vezes mais barato em output), `gpt-4o`. OpenRouter: `openai/gpt-5-mini`, `openai/gpt-4o-mini`, etc. | `gpt-5-mini` |
| `OPENAI_API_BASE` | Base URL da API. Só defina se usar **OpenRouter**: `https://openrouter.ai/api/v1`. O `gpt_engine` já usa como `base_url`. | — |
| `ALLOWED_ORIGINS` | Origens CORS extras, separadas por vírgula. O backend já inclui `*.up.railway.app` e localhost. | — |

### Definidas pelo Railway (não crie)

- `PORT` — o Railway define automaticamente para o serviço web.

---

## OpenRouter (alternativa à OpenAI)

O [OpenRouter](https://openrouter.ai) oferece acesso a vários modelos (OpenAI, Anthropic, Google, etc.) por uma única API compatível com OpenAI.

### Variáveis para usar OpenRouter

| Variável | Valor | Onde obter |
|----------|-------|------------|
| `API_OPENAI_KEY_RESEARCH` | Sua chave OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `OPENAI_API_BASE` | `https://openrouter.ai/api/v1` | Fixo |
| `OPENAI_MODEL` | ID do modelo no OpenRouter, ex.: `openai/gpt-5-mini`, `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet`, `google/gemini-2.0-flash` | [openrouter.ai/models](https://openrouter.ai/models) |

### Exemplo no Railway (Variables do backend)

```
API_OPENAI_KEY_RESEARCH=sk-or-v1-xxxxxxxx
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-5-mini
```

**Nota:** O `gpt_engine` já usa `OPENAI_API_BASE` como `base_url` quando a variável está definida. O OpenRouter expõe a API **Chat Completions**; se o código usar outra (ex.: Responses), pode ser preciso adaptar as chamadas.

---

## Como vincular o Postgres do Railway ao Backend

O Postgres fica como um **serviço (Database)** no mesmo projeto. Para o backend usar o banco **sem** copiar e colar a URL:

### 1. Criar o Postgres (se ainda não existe)

1. No **projeto** do Railway, clique em **+ New**.
2. Escolha **Database** → **PostgreSQL**.
3. O Railway cria o serviço e expõe variáveis como `DATABASE_URL`, `PGHOST`, `PGPORT`, etc.

### 2. Vincular o Postgres ao serviço da API

1. Clique no **serviço do Backend (API)** — não no Postgres.
2. Abra a aba **Variables** (Variáveis).
3. Clique em **+ New Variable** ou **Add Variable**.
4. Escolha **Add a Reference** (ou **Variable Reference** / **Referência**).
5. Em **Service**, selecione o **Postgres** (o nome do serviço do banco que você criou).
6. Em **Variable** (ou **Variável**), selecione **`DATABASE_URL`** (ou `DATABASE_PRIVATE_URL` se existir e quiser tráfego só na rede interna).
7. Em **Variable Name** (nome no backend), deixe **`DATABASE_URL`** — é o que o `database.py` usa.
8. Confirme ( **Add** / **Add Variable** ).

O Railway passa a injetar `DATABASE_URL` no backend com o valor do Postgres. Se o Postgres for recriado ou a senha mudar, a referência continua válida.

### 3. Resumo visual

```
[Projeto Railway]
  ├── Postgres (Database)  →  expõe DATABASE_URL, PGHOST, PGPORT, ...
  └── Backend (API)       →  Variables: DATABASE_URL = Referência → Postgres.DATABASE_URL
```

### 4. Se não houver “Add a Reference”

- Em **Variables** do backend: **New Variable** → no dropdown ou em **Link**, procure **From Service** / **From Database** / **Connect** e escolha o Postgres e a variável `DATABASE_URL`.

### 5. Conferir

Após o vínculo, em **Variables** do backend deve aparecer algo como `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` ou um ícone de link. Não é uma string longa `postgresql://...` que você colou — é uma referência. O valor real só é resolvido em tempo de deploy.

---

## Serviço Frontend (se estiver no Railway)

No **serviço do frontend**, em **Variables**:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | URL base da API (backend). | `https://medquest-research-api.up.railway.app` |

Use a URL real do seu backend (domínio do Railway ou custom).

---

## Resumo rápido (backend)

**Mínimo (OpenAI):**

```
DATABASE_URL=postgresql://...   (ou referência ao Postgres do Railway)
API_OPENAI_KEY_RESEARCH=sk-proj-...
```

**Mínimo (OpenRouter):**

```
DATABASE_URL=postgresql://...   (ou referência ao Postgres do Railway)
API_OPENAI_KEY_RESEARCH=sk-or-v1-...
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-5-mini
```

(O `gpt_engine` já suporta `OPENAI_API_BASE`.)

**Opcional (o padrão já é `gpt-5-mini`):**

```
OPENAI_MODEL=gpt-5-mini
# ou gpt-4o-mini se quiser priorizar custo em respostas longas
ALLOWED_ORIGINS=https://...
```

---

## Sobre o GPT-5 mini

O **gpt-5-mini** é o modelo padrão no `gpt_engine`: versão mais rápida e econômica do GPT-5, indicada para tarefas bem definidas (explicar conceitos, análise crítica, fatos, etc.). Contexto de 400k tokens, suporte a Chat Completions e Responses API. Preços (OpenAI): input ~US$ 0,25/1M tokens, output ~US$ 2,00/1M tokens. Se o foco for **só custo** em respostas muito longas, `gpt-4o-mini` pode ser mais barato no output; para melhor custo-benefício em capacidade, use `gpt-5-mini`.

---

## Observações

- `GROQ_API_KEY` e `GEMINI_API_KEY` aparecem no `.env.example`, mas **não são usadas** pelo código atual.
- Nunca faça commit de `.env` ou `.env.local` com chaves. Use apenas **Variables** no Railway.
- O `gpt_engine` já usa `OPENAI_API_BASE` como `base_url` quando a variável está definida (suporte a OpenRouter).
