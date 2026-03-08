# Análise: ANALYSIS_PIPELINE.md × Implementação Atual

Este documento analisa o `ANALYSIS_PIPELINE.md` em relação ao código do MedQuestResearch: o que está alinhado, o que diverge e o que falta.

---

## 1. Resumo do ANALYSIS_PIPELINE.md

O pipeline descrito tem **6 etapas** em sequência:

| Etapa | Nome | Objetivo | Saída esperada |
|-------|------|----------|----------------|
| 1 | Visualizar Estrutura | Identificar seções do artigo | JSON: title, abstract, sections[], tables_detected, figures_detected |
| 2 | Mapeamento PICO | Extrair estrutura científica | JSON: population, intervention, comparator, outcomes[], study_design |
| 3 | Extração de Dados | Dados quantitativos para metanálise | JSON: study_metadata, population, outcomes[] (mean/sd/n) |
| 4 | Análise Crítica | Qualidade metodológica | Relatório crítico estruturado |
| 5 | Risco de Viés | RoB2 / ROBINS-I | JSON: tool_used, domains, overall_risk |
| 6 | Preparação para Metanálise | Normalizar para meta_stats | JSON: study_id, outcome, n_intervention, mean_intervention, sd_intervention, n_control, mean_control, sd_control |

O doc também define:

- **Backend:** `api.py` → `research_jobs.py` → `gpt_engine.py` → analysis modules  
- **Banco:** tabela `analysis_results` com `article_id`, `structure_json`, `pico_json`, `data_extraction_json`, `bias_json`, `critical_analysis_text`  
- **Evidence Graph:** como “Futuro” (Study → Population, Intervention, Outcome, Effect)

---

## 2. Mapeamento: Doc × Código Atual

### Etapa 1 — Visualizar Estrutura

| Doc | Atual |
|-----|--------|
| Saída: JSON com `title`, `abstract`, `sections[]`, `tables_detected`, `figures_detected` | **structure_visualizer.py**: retorna **texto** (descrição para “fluxograma/mapa mental”), não JSON estruturado. Nenhum schema JSON obrigatório. |

**Conclusão:** Objetivo semelhante (estrutura do artigo), mas **formato diferente**. O doc pede JSON reutilizável; o código gera narrativa em texto.

---

### Etapa 2 — Mapeamento Científico (PICO)

| Doc | Atual |
|-----|--------|
| Saída: JSON `population`, `intervention`, `comparator`, `outcomes[]`, `study_design` | **structure_mapper.py**: retorna **texto** (mapa de seções/subseções e fluxo lógico), **não** PICO. PICO é extraído em **prisma_analyzer.py** (campo `pico`) e no fluxo de **meta_analysis** (Etapa 1). |

**Conclusão:** O **nome** “structure_mapper” no código refere-se a “mapa da estrutura do documento”. O **PICO** do doc está implementado no **prisma_analyzer** e na **metanálise (etapa 1)**, não no `structure_mapper.py`.

---

### Etapa 3 — Extração de Dados

| Doc | Atual |
|-----|--------|
| JSON: study_metadata, population (total_sample_size, intervention_group_n, control_group_n), outcomes (name, intervention_mean, control_mean, effect_type) | **prisma_analyzer.py**: retorna `quantitative_outcomes` com `outcome_name`, `measure_type`, `intervention_group` / `control_group` (n, mean, sd, events, percentage), `effect_measure` (or, rr, ci, p_value). **evidence_graph_service** e **meta_analysis** consomem esse JSON (e formato compatível da Etapa 2 da metanálise). |

**Conclusão:** **Alinhado em espírito.** O schema real é mais rico (PRISMA + effect_measure); o doc pode ser atualizado para refletir `quantitative_outcomes` e nomes atuais.

---

### Etapa 4 — Análise Crítica

| Doc | Atual |
|-----|--------|
| Relatório crítico (validade interna, viés, limitações, aplicabilidade) | **critical_analysis.py**: `aplicar_leitura_critica(texto, foco_analise)` retorna texto. Usado em job assíncrono. |

**Conclusão:** **Alinhado.** Não há JSON definido no doc para esta etapa; texto é coerente.

---

### Etapa 5 — Risco de Viés (RoB2 / ROBINS-I)

| Doc | Atual |
|-----|--------|
| JSON: tool_used, domains (randomization, deviations, missing_data, measurement, reporting), overall_risk | **prisma_analyzer.py**: retorna `risco_vies` (Low/Some_concerns/High/Insufficient_information) e `checklist_prisma`. Não há domínios RoB2/ROBINS-I explícitos em JSON separado. |

**Conclusão:** **Parcial.** Avaliação de viés existe (PRISMA + escore), mas não no formato “domains” do doc. Um módulo dedicado RoB2/ROBINS-I em JSON seria uma evolução.

---

### Etapa 6 — Preparação para Metanálise

| Doc | Atual |
|-----|--------|
| JSON: study_id, outcome, n_intervention, mean_intervention, sd_intervention, n_control, mean_control, sd_control | **meta_stats.py**: recebe dados nesse formato (Effect com study_id, label, e cálculos SMD/OR/RR). **evidence_graph_service** monta nós/edges a partir do JSON de extração; **meta_analysis** + **meta_detector** usam esse fluxo. |

**Conclusão:** **Alinhado.** O formato do doc é o que o motor estatístico e o evidence graph consomem.

---

## 3. Backend e Banco de Dados

### Fluxo backend (doc)

```text
api.py → research_jobs.py → gpt_engine.py → analysis modules
```

**Atual:** Não existe arquivo **research_jobs.py**. Toda a lógica de jobs (`processar_job_*`, INSERT/UPDATE em `research_jobs`) está em **api.py**. O doc reflete uma arquitetura alvo (jobs em módulo separado).

### Tabela analysis_results (doc)

Campos: `article_id`, `structure_json`, `pico_json`, `data_extraction_json`, `bias_json`, `critical_analysis_text`.

**Atual:** Essa tabela **não existe**. O sistema usa:

- **research_jobs**: `entrada`, `resultado`, `dados_extras` (JSON), `project_id`  
- Resultados de análise (incl. PRISMA e extração) ficam em `resultado` (texto) ou dentro de `dados_extras` (ex.: artigos com `analise_prisma`).  
- Nada é persistido em colunas dedicadas por etapa (structure_json, pico_json, etc.).

**Conclusão:** O doc descreve um **modelo de persistência por etapa** que ainda não foi implementado. Hoje os dados são “por job” e em JSON livre em `dados_extras`.

---

## 4. Evidence Graph

| Doc | Atual |
|-----|--------|
| “Futuro” — Study → Population, Intervention, Outcome, Effect | **Já implementado** em `services/evidence_graph_service.py`: build_graph_from_extraction_json, carregar_evidence_graph_por_projeto, studies_for_outcome, detectar_metaanalises_possiveis (via meta_detector). |

**Conclusão:** O doc está desatualizado: Evidence Graph não é mais “futuro”, é parte do fluxo atual (metanálise Etapa 2, upload_articles, meta_detector).

---

## 5. Fluxo real vs pipeline do doc

- **Doc:** pipeline **sequencial** por artigo (Estrutura → PICO → Extração → Crítica → Viés → Preparação Metanálise), com cada etapa gerando JSON e gravando em `analysis_results`.
- **Atual:**
  - **Por artigo (dashboard):** módulos **independentes** (visualizar estrutura, mapa, crítica, fatos, etc.) sob demanda; saídas em texto ou JSON livre em `research_jobs.resultado` / `dados_extras`.
  - **Metanálise (upload):** upload múltiplo → **prisma_analyzer** em lote (estrutura + PICO + extração + viés em um passo) → resultado em memória e em `dados_extras`; Evidence Graph atualizado na Etapa 2 da metanálise.
  - Não há “um” pipeline fixo de 6 etapas por artigo nem tabela `analysis_results`.

---

## 6. Checklist de alinhamento

| Item | Status |
|------|--------|
| Etapa 1 (estrutura) em JSON (title, abstract, sections, tables, figures) | ❌ Código retorna texto |
| Etapa 2 (PICO) em JSON por structure_mapper | ❌ PICO está no prisma_analyzer / meta_analysis |
| Etapa 3 (extração) em JSON | ✅ prisma_analyzer + meta_analysis (formato mais rico) |
| Etapa 4 (análise crítica) | ✅ critical_analysis.py |
| Etapa 5 (RoB2/ROBINS-I em JSON com domains) | ⚠️ Parcial (risco_vies + checklist PRISMA) |
| Etapa 6 (formato para meta_stats) | ✅ meta_stats + evidence graph |
| research_jobs.py separado | ❌ Tudo em api.py |
| Tabela analysis_results | ❌ Não existe |
| Evidence Graph | ✅ Implementado (doc diz “Futuro”) |

---

## 7. Recomendações

### 7.1 Atualizar o ANALYSIS_PIPELINE.md (recomendado)

- **Etapa 1:** Documentar que “Visualizar Estrutura” hoje é **structure_visualizer** com saída em **texto**; opcionalmente descrever um JSON alvo para evolução.
- **Etapa 2:** Esclarecer que “Mapeamento PICO” é feito pelo **prisma_analyzer** (e Etapa 1 da metanálise), e que **structure_mapper** é “mapa da estrutura do documento” (seções), não PICO.
- **Etapa 3:** Alinhar o schema de exemplo ao **quantitative_outcomes** do prisma_analyzer (e ao JSON da Etapa 2 da metanálise).
- **Etapa 5:** Manter RoB2/ROBINS-I como evolução; mencionar que hoje temos `risco_vies` + checklist PRISMA.
- **Backend:** Indicar que a orquestração de jobs está em **api.py** e que **research_jobs.py** é uma refatoração futura.
- **Banco:** Documentar que hoje se usa **research_jobs** (entrada/resultado/dados_extras) e que **analysis_results** é modelo alvo para persistência por etapa.
- **Evidence Graph:** Mover de “Futuro” para “Implementado” e referenciar `services/evidence_graph_service.py` e integração com metanálise.

### 7.2 Evolução do código (opcional)

- **structure_visualizer:** Adicionar modo ou função que retorne JSON (title, abstract, sections, tables_detected, figures_detected) para compatibilidade com o pipeline do doc.
- **structure_mapper:** Ou renomear para evitar confusão com PICO, ou adicionar uma função “PICO only” que retorne o JSON da Etapa 2 do doc (e usar onde fizer sentido).
- **Tabela analysis_results:** Criar migration e passar a gravar resultados por etapa quando existir um “pipeline completo” por artigo (ex.: após upload ou após rodar sequência de módulos).
- **research_jobs.py:** Extrair de api.py a lógica de processamento de jobs para um módulo separado, como no doc.

---

## 8. Conclusão

O **ANALYSIS_PIPELINE.md** descreve um pipeline **ideal** (6 etapas, JSON por etapa, tabela `analysis_results`, Evidence Graph como futuro). Na prática:

- Várias etapas existem, mas com **nomes/limites diferentes** (estrutura e PICO em texto ou dentro do PRISMA).
- A **extração para metanálise** e o **Evidence Graph** já estão implementados e em uso.
- **Persistência** é por job (`research_jobs`), não por artigo/etapa (`analysis_results`).

Recomendação principal: **atualizar o ANALYSIS_PIPELINE.md** para refletir o fluxo atual (módulos, PRISMA em lote, Evidence Graph, research_jobs) e marcar claramente o que é “estado atual” e o que é “modelo alvo” (JSON por etapa, analysis_results, research_jobs.py). Isso alinha a documentação à base de código e evita expectativas incorretas.
