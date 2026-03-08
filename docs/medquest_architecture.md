
# MedQuestResearch — Arquitetura do Sistema de Análise de Artigos e Metanálise

Este documento descreve a arquitetura recomendada do MedQuestResearch, considerando os módulos já existentes no projeto e a separação da metanálise como módulo independente acionado por botão/modal.

Objetivos da arquitetura:

- manter análises de artigo separadas da metanálise
- garantir pipeline científico estruturado
- facilitar manutenção e evolução do sistema
- permitir expansão futura (Evidence Graph, Auto‑MetaAnalysis)

---

# 1. Visão Geral da Arquitetura

Fluxo conceitual do sistema:

PDF / TEXTO DO ARTIGO  
        │  
        ▼  
CORE ENGINE (parser + indexação texto)  
        │  
        ▼  
BANCO DE ARTIGOS  
        │  
        ├── Estrutura Viewer  
        ├── Mapeamento do Artigo  
        └── Análise Crítica  

Módulo independente:

META‑ANALYSIS MODULE (botão/modal)

---

# 2. Estrutura do Backend (atual e recomendada)

backend/
│
├── api.py                    # Rotas + orquestração; lógica de jobs pode ser extraída para research_jobs.py
├── gpt_engine.py
├── model_router.py
├── cache_llm.py
│
├── pdf_processor.py          # Core: extração de texto (PDF/DOCX) — equivalente a "article_parser"
│
├── structure_visualizer.py   # Visualizar estrutura do artigo (título, abstract, métodos, etc.)
├── structure_mapper.py       # Mapeamento PICO
│
├── critical_analysis.py
├── prisma_analyzer.py
│
├── meta_analysis.py
├── meta_stats.py
├── meta_detector.py          # Detecção de metanálises possíveis a partir do Evidence Graph
│
├── services/
│   ├── evidence_graph_service.py   # Evidence Graph (Study → Population, Intervention, Outcome, Effect)
│   ├── credit_service.py
│   └── __init__.py
├── routes/
│   ├── asaas_webhook.py
│   ├── checkout_creditos.py
│   └── __init__.py
│
├── database.py
├── auth.py
├── chunker.py
├── explain_concept.py
├── Fact_checker.py
├── literature_search.py
├── pubmed_client.py
├── migrations/
│
└── utils/                    # (recomendado criar) funções compartilhadas

---

# 3. Core Engine

Arquivo principal:

pdf_processor.py (função de article parser)

Responsável por:

- extrair texto do PDF
- identificar seções
- normalizar texto
- salvar artigo no banco

Fluxo:

Upload PDF  
↓  
Parser  
↓  
Texto estruturado  
↓  
Banco de dados

---

# 4. Módulos de Análise de Artigo

Cada botão da interface executa um módulo independente.

## 4.1 Visualizar Estrutura do Artigo

Arquivo:

structure_visualizer.py

Função:

Identificar automaticamente:

- título
- abstract
- introdução
- métodos
- resultados
- discussão
- referências

Saída:

estrutura hierárquica do artigo

---

## 4.2 Mapeamento Científico

Arquivo:

structure_mapper.py

Detecta:

- PICO
- Population
- Intervention
- Comparator
- Outcome

Saída exemplo:

{
  "population": "",
  "intervention": "",
  "comparator": "",
  "outcomes": []
}

---

## 4.3 Análise Crítica Científica

Arquivo:

critical_analysis.py

Utiliza:

gpt_engine.py

Avalia:

- validade metodológica
- limitações
- risco de viés
- validade externa

Saída:

relatório crítico do estudo

---

## 4.4 Verificação PRISMA

Arquivo:

prisma_analyzer.py

Função:

Avaliar completude de relato conforme PRISMA.

Verifica:

- descrição da busca
- critérios de inclusão
- seleção de estudos
- avaliação de viés
- síntese de resultados

Importante:

PRISMA avalia qualidade do relato, não risco de viés.

---

# 5. Módulo de Metanálise

Acionado por botão/modal:

Executar Meta‑Análise

Fluxo:

Selecionar artigos  
↓  
Selecionar desfecho  
↓  
Confirmar dados extraídos  
↓  
Executar metanálise

---

# 6. Arquitetura da Metanálise

Arquivo principal:

meta_analysis.py

Motor estatístico:

meta_stats.py

Fluxo:

dados confirmados  
↓  
meta_stats  
↓  
pool_effects  
↓  
forest_plot  
↓  
interpretação científica

---

# 7. Motor Estatístico

Arquivo:

meta_stats.py

Responsável por:

- calcular effect size
- calcular heterogeneidade
- gerar forest plot

Métodos:

- effect_smd_hedges_g
- effect_log_rr
- effect_log_or

Modelos:

- fixed effects
- random effects (DerSimonian‑Laird)

---

# 8. Estrutura do Banco de Dados

**Nota:** Na implementação atual, o fluxo de análise e metanálise usa principalmente a tabela `research_jobs` (entrada, resultado, dados_extras, project_id). As tabelas abaixo são o modelo alvo para evolução futura (persistência de artigos e projetos de metanálise).

Tabela: articles

Campos:

id  
title  
authors  
year  
doi  
text  
parsed_structure  

Tabela: article_analysis

Campos:

article_id  
structure_map  
critical_analysis  
prisma_report  

Tabela: meta_projects

Campos:

id  
title  
research_question  
effect_measure  
created_at  

Tabela: meta_studies

Campos:

meta_id  
article_id  
outcome_name  
mean_intervention  
sd_intervention  
n_intervention  
mean_control  
sd_control  
n_control  

---

# 9. Arquitetura Geral

USER  
↓  
FRONTEND  
↓  
API SERVER  
↓  
ARTICLE ANALYSIS + META ANALYSIS  
↓  
POSTGRESQL  
↓  
Evidence Graph

---

# 10. Evidence Graph

Arquivo (implementado):

services/evidence_graph_service.py

Estrutura:

Study  
 ├ Population  
 ├ Intervention  
 ├ Outcome  
 └ Effect  

Benefícios:

- relacionar estudos automaticamente
- detectar outcomes semelhantes
- sugerir metanálises automaticamente

---

# 11. Auto‑MetaAnalysis Detection

Algoritmo:

Se ≥ 3 estudos com mesmo outcome  
→ sugerir metanálise

---

# 12. Checklist para Revisão no Cursor

1. ✅ Módulos existem (pdf_processor, structure_visualizer, structure_mapper, critical_analysis, prisma_analyzer, meta_analysis, meta_stats, services/evidence_graph_service).
2. Garantir responsabilidades claras.
3. ✅ Separar claramente: article analysis vs meta analysis.
4. ✅ Evidence Graph em services/evidence_graph_service.py.
5. ✅ Metanálise via modal/etapas no frontend.
6. (Opcional) Criar backend/utils/ para funções compartilhadas.
7. (Opcional) Extrair lógica de jobs de api.py para research_jobs.py.

---

# Conclusão

A arquitetura permite que o MedQuestResearch funcione como:

Plataforma completa de análise científica  
+  
Ferramenta automatizada de metanálise

Com separação clara entre:

Análise de Artigos  
Metanálise
