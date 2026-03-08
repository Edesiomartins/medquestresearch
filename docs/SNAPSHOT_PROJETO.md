## Snapshot Compacto – MedQuestResearch

### Stack
- **Backend**: FastAPI (Python) com jobs assíncronos e sistema de créditos.
- **Frontend**: Next.js (App Router) com dashboard, fluxo de metanálise PRISMA e página de planos.

---

### 1. Rotas principais do Backend

#### Autenticação / Usuário
- `POST /genapi/cadastro`
- `POST /genapi/login`
- `GET  /genapi/creditos` – retorna créditos totais, usados e disponíveis.

#### Jobs Assíncronos
- `GET  /genapi/job/{job_id}` – status/resultado de um job.
- `GET  /genapi/jobs` – lista jobs do usuário.

#### Módulos IA (jobs assíncronos)
- `POST /genapi/pdf` – upload + extração de texto de 1 arquivo.
- `POST /genapi/explicar`
- `POST /genapi/critica`
- `POST /genapi/fatos`
- `POST /genapi/perspectiva`
- `POST /genapi/mapa`
- `POST /genapi/structure_mapper`
- `POST /genapi/structure_visualizer`

#### Metanálise PRISMA
- `POST /genapi/meta_analysis` – metanálise por etapas (1–4).
- `POST /genapi/meta_analise` – alias compatível.
- `POST /genapi/meta_analysis/upload_articles` – upload múltiplo + análise PRISMA por artigo (síncrono).

#### Admin
- `GET  /genapi/admin/custos` – lista custos (créditos) por módulo.
- `POST /genapi/admin/adicionar-creditos` – adiciona créditos a um usuário.

#### Monetização (público / estático)
- `GET  /genapi/planos` – lista planos mensais.
- `GET  /genapi/pacotes` – lista pacotes avulsos de créditos.

---

### 2. Payloads principais

#### 2.1 Upload múltiplo + PRISMA
**Endpoint:** `POST /genapi/meta_analysis/upload_articles`  
**Auth:** Bearer `<token>`  
**Content-Type:** `multipart/form-data`

Campos:
- `files`: múltiplos arquivos PDF/DOCX (até 15, todos com o mesmo nome de campo).

Resposta (shape):

```json
{
  "resultado": "Artigos processados e analisados com sucesso",
  "total_artigos": 5,
  "artigos": [
    {
      "filename": "artigo1.pdf",
      "titulo": "Título do Artigo",
      "texto_extraido_chars": 12345,
      "analise_prisma": {
        "study_type": "RCT",
        "pico": {
          "population": "string|not_reported",
          "intervention": "string|not_reported",
          "comparison": "string|not_reported",
          "outcomes": ["..."]
        },
        "quantitative_outcomes": [
          {
            "outcome_name": "string",
            "measure_type": "mean_sd|n_percentage|or_ci|rr_ci|other",
            "intervention_group": { "n": "integer|not_reported", "mean": "number|not_reported", "sd": "number|not_reported", "events": "integer|not_reported", "percentage": "number|not_reported" },
            "control_group": { "n": "integer|not_reported", "mean": "number|not_reported", "sd": "number|not_reported", "events": "integer|not_reported", "percentage": "number|not_reported" }
          }
        ],
        "checklist_prisma": {},
        "risco_vies": "Low|Some_concerns|High|Insufficient_information",
        "pontuacao_prisma": 12,
        "escore_qualidade": 8,
        "justificativa_escore": "string",
        "pontos_fortes": ["..."],
        "pontos_fracos": ["..."],
        "recomendacao": "Include|Exclude|Include_with_reservations",
        "observacoes": "string"
      }
    }
  ],
  "resumo_analises": {
    "escore_medio": 7.5,
    "pontuacao_prisma_media": 11.2,
    "artigos_por_qualidade": {
      "excelente": 2,
      "boa": 2,
      "regular": 1,
      "baixa": 0
    }
  }
}
```

**Créditos (default):**
- Upload PDF: `CREDIT_COST_PDF` (3) por arquivo.
- Análise PRISMA/metanálise: `CREDIT_COST_META_ANALISE` (12) por artigo.
- Total default ≈ **15 créditos por artigo**.

#### 2.2 Metanálise por etapas (1–4)
**Endpoint:** `POST /genapi/meta_analysis` (ou `/genapi/meta_analise`)  
**Auth:** Bearer `<token>`  
**Content-Type:** `application/json`

Body:

```json
{
  "tema": "string (pode ser vazio no novo fluxo)",
  "etapa": "1|2|3|4",
  "texto_artigo": "string|null",
  "json_extracao": "string|object|null",
  "estilo": "Vancouver|ABNT",
  "manuscrito": "string|null",
  "artigos_analisados": "JSON string ou objeto/lista com análises PRISMA"
}
```

Resposta inicial (assíncrona):

```json
{
  "request_id": 123,
  "status": "processing",
  "etapa": "1"
}
```

Polling `GET /genapi/job/{request_id}`:

```json
{
  "status": "done",
  "resultado": "string",
  "erro": null,
  "artigos": [...],
  "total_artigos": 10
}
```

**Créditos (default):** `CREDIT_COST_META_ANALISE` (12) por etapa/job.

---

### 3. Variáveis de ambiente críticas

#### LLM / OpenRouter
- `API_OPENAI_KEY_RESEARCH=<chave OpenRouter>`
- `OPENAI_API_BASE=https://openrouter.ai/api/v1`
- `OPENAI_MODEL=nvidia/nemotron-nano-12b-v2-vl:free`
- `OPENAI_MODEL_FALLBACK=openai/gpt-4o-mini,openai/gpt-3.5-turbo,anthropic/claude-3-haiku`
- `OPENROUTER_MAX_OUTPUT_TOKENS=1000`
- `OPENROUTER_REFERRER=https://medquestresearch.up.railway.app`
- `OPENROUTER_TITLE=MedQuestResearch`

#### Custos em créditos (opcionais, defaults em `backend/credit_costs.py`)
- `CREDIT_COST_PDF=3`
- `CREDIT_COST_EXPLICAR=5`
- `CREDIT_COST_CRITICA=7`
- `CREDIT_COST_FATOS=5`
- `CREDIT_COST_PERSPECTIVA=10`
- `CREDIT_COST_MAPA=8`
- `CREDIT_COST_STRUCTURE_MAPPER=6`
- `CREDIT_COST_STRUCTURE_VISUALIZER=8`
- `CREDIT_COST_META_ANALISE=12`

#### Banco de dados
- `DATABASE_URL=postgresql://usuario:senha@host:porta/database`

---

### 4. UX rápida do Frontend

- Dashboard (`/`): upload de PDF, seleção de módulo (explicar, crítica, fatos, perspectiva, metanálise, etc.).
- Metanálise PRISMA:
  - Modo metanálise na janela esquerda (`TextWindow`):
    - Botão "Selecionar arquivos" (até 15 PDFs/DOCX).
    - Botão "Iniciar Análise PRISMA" → chama `/meta_analysis/upload_articles`.
  - Janela direita (`ResultPanel`):
    - Mostra resumo PRISMA.
    - Botão "Continuar para Etapa 2, 3 e 4" → chama `/meta_analysis` etapas 2–4 com `artigos_analisados`.
- Página de monetização: `/planos` (consome `GET /genapi/planos` e `GET /genapi/pacotes`).

