# Análise: medquest_architecture.md × Estrutura Atual do Projeto

Este documento compara a arquitetura definida em `medquest_architecture.md` com o estado atual do MedQuestResearch e propõe ações para adequar a estrutura.

---

## 1. Visão geral (arquitetura × realidade)

| Aspecto | Arquitetura (doc) | Projeto atual | Alinhado? |
|--------|--------------------|---------------|-----------|
| Core engine (parser + indexação) | `article_parser.py` | `pdf_processor.py` (extração PDF + DOCX) | ⚠️ Nome diferente |
| Estrutura do artigo | `structure_viewer.py` | `structure_visualizer.py` | ⚠️ Nome diferente |
| Mapeamento PICO | `structure_mapper.py` | `structure_mapper.py` | ✅ |
| Análise crítica | `critical_analysis.py` | `critical_analysis.py` | ✅ |
| PRISMA | `prisma_analyzer.py` | `prisma_analyzer.py` | ✅ |
| Metanálise | `meta_analysis.py` | `meta_analysis.py` | ✅ |
| Motor estatístico | `meta_stats.py` | `meta_stats.py` | ✅ |
| Evidence Graph | `evidence_graph.py` (raiz backend) | `services/evidence_graph_service.py` | ⚠️ Local + nome |
| Jobs assíncronos | `research_jobs.py` | Lógica dentro de `api.py` | ⚠️ Não separado |
| API | `api.py` | `api.py` | ✅ |
| GPT | `gpt_engine.py` | `gpt_engine.py` | ✅ |
| Utilitários | `utils/` | Não existe | ❌ Falta |

---

## 2. Estrutura de pastas: doc × atual

### 2.1 Doc (recomendado)

```
backend/
├── api.py
├── research_jobs.py
├── gpt_engine.py
├── article_parser.py
├── structure_viewer.py
├── structure_mapper.py
├── critical_analysis.py
├── prisma_analyzer.py
├── meta_analysis.py
├── meta_stats.py
├── evidence_graph.py
└── utils/
```

### 2.2 Atual

```
backend/
├── api.py
├── gpt_engine.py
├── model_router.py
├── cache_llm.py
├── pdf_processor.py          ← equivalente a article_parser
├── structure_visualizer.py   ← equivalente a structure_viewer
├── structure_mapper.py
├── critical_analysis.py
├── prisma_analyzer.py
├── meta_analysis.py
├── meta_stats.py
├── meta_detector.py
├── services/
│   ├── evidence_graph_service.py  ← equivalente a evidence_graph
│   ├── credit_service.py
│   └── __init__.py
├── routes/
│   ├── asaas_webhook.py
│   ├── checkout_creditos.py
│   └── __init__.py
├── migrations/
├── database.py
├── auth.py
├── chunker.py
├── explain_concept.py
├── Fact_checker.py
├── literature_search.py
├── Perspective_research.py
├── pubmed_client.py
├── asaas_client.py
├── credit_costs.py
├── adicionar_creditos.py
└── (não existe utils/)
```

---

## 3. Banco de dados (doc × atual)

### 3.1 Doc

- **articles**: id, title, authors, year, doi, text, parsed_structure  
- **article_analysis**: article_id, structure_map, critical_analysis, prisma_report  
- **meta_projects**: id, title, research_question, effect_measure, created_at  
- **meta_studies**: meta_id, article_id, outcome_name, mean_intervention, sd_intervention, n_intervention, mean_control, sd_control, n_control  

### 3.2 Atual

- **research_jobs**: usado para jobs assíncronos (usuario_id, modulo, status, entrada, resultado, creditos, dados_extras, project_id, etc.).  
- **pagamentos**, **historico_creditos**: monetização.  
- Tabelas `articles`, `article_analysis`, `meta_projects`, `meta_studies` **não aparecem** nas migrations atuais; o fluxo de metanálise usa `research_jobs` (entrada/resultado/dados_extras) e `project_id` para agrupar.

**Conclusão:** O modelo de dados do doc (artigos persistentes + análises + projetos de metanálise) não está implementado como descrito. Hoje o sistema é orientado a jobs e payloads em JSON, não a entidades `articles`/`meta_studies` normalizadas.

---

## 4. Checklist da arquitetura (doc §12) × estado

| Item | Estado |
|------|--------|
| 1. Confirmar se os módulos existem | ✅ Existem, com nomes/locais diferentes em alguns casos |
| 2. Garantir responsabilidades claras | ✅ Módulos têm responsabilidades definidas |
| 3. Separar article analysis vs meta analysis | ✅ Rotas e módulos já separados (metanálise via modal/etapas) |
| 4. Criar módulo evidence_graph.py | ⚠️ Existe como `services/evidence_graph_service.py` |
| 5. Garantir metanálise via modal | ✅ Frontend já usa fluxo por etapas/modal |

---

## 5. Plano de adequação da estrutura

### 5.1 Opção A – Alinhar nomes ao documento (refatoração)

- Renomear `pdf_processor.py` → `article_parser.py` (e manter/encapsular extração PDF/DOCX dentro dele).  
- Renomear `structure_visualizer.py` → `structure_viewer.py`.  
- Criar `evidence_graph.py` na raiz de `backend/` que importa e reexpõe a API de `services/evidence_graph_service.py` (facade), para manter compatibilidade com o doc sem duplicar lógica.

Impacto: atualizar todos os imports em `api.py` e em outros módulos que usam esses nomes.

### 5.2 Opção B – Atualizar o documento (recomendado)

- Atualizar `medquest_architecture.md` para refletir os nomes atuais:
  - `article_parser.py` → **pdf_processor.py** (parser de PDF/DOCX + extração de texto).
  - `structure_viewer.py` → **structure_visualizer.py**.
  - `evidence_graph.py` → **services/evidence_graph_service.py**.
- Documentar que a lógica de jobs está em **api.py** (e opcionalmente extrair para `research_jobs.py` depois).
- Documentar a pasta **services/** e **routes/** na estrutura do backend.

Vantagem: zero quebra de código; o doc fica alinhado à base atual.

### 5.3 Melhorias independentes da opção

1. **Criar `backend/utils/`**  
   - Mover funções genéricas (normalização de texto, formatação, constantes compartilhadas) para módulos em `utils/` e importar de lá.  
   - Reduz acoplamento e deixa a estrutura mais próxima do doc.

2. **Opcional: extrair `research_jobs.py`**  
   - Mover de `api.py` para um módulo `research_jobs.py` as funções `processar_job_*` e a lógica de atualização de `research_jobs`.  
   - `api.py` apenas chama funções de `research_jobs` e define as rotas.  
   - Deixa a arquitetura igual ao desenho do doc (api + research_jobs separados).

3. **Banco de dados (futuro)**  
   - Se quiser evoluir para o modelo do doc (artigos persistentes, projetos de metanálise, meta_studies):  
     - Criar migrations para `articles`, `article_analysis`, `meta_projects`, `meta_studies`.  
     - Migrar gradualmente: passar a persistir resultados de upload/análise em `articles` + `article_analysis` e a preencher `meta_studies` quando houver metanálise.  
   - Hoje não é obrigatório para “adequar a estrutura”; é evolução de modelo de dados.

---

## 6. Resumo executivo

- **Análise de artigos** e **metanálise** já estão separados na prática (módulos e fluxo de UI).  
- A maior diferença é **nomenclatura** (article_parser/pdf_processor, structure_viewer/structure_visualizer, evidence_graph vs services/evidence_graph_service) e **local** do Evidence Graph.  
- **research_jobs**: lógica dentro de `api.py`; o doc prevê arquivo separado `research_jobs.py`.  
- **Banco**: modelo do doc (articles, article_analysis, meta_projects, meta_studies) não implementado; hoje tudo gira em torno de `research_jobs` e payloads JSON.  

**Recomendações imediatas:**  
1. Atualizar `medquest_architecture.md` para os nomes e pastas atuais (Opção B).  
2. Criar `backend/utils/` e começar a concentrar helpers lá.  
3. Opcional: extrair a lógica de jobs para `research_jobs.py`.  
4. Deixar a migração para o modelo de dados “articles + meta_projects/meta_studies” como passo futuro, quando quiser persistir artigos e projetos de metanálise de forma normalizada.

Se quiser, posso propor um patch concreto para o `medquest_architecture.md` (seção 2 e checklist) refletindo a Opção B e a estrutura atual.
