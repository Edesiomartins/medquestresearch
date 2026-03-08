# MedQuestResearch --- Analysis Pipeline

Este documento define o **pipeline completo de análise científica** do
MedQuestResearch.

Ele descreve:

-   etapas do processamento de artigos
-   formatos JSON padronizados
-   prompts recomendados para LLM
-   integração com metanálise
-   arquitetura de execução

O objetivo é garantir **saídas estruturadas, científicas e
reutilizáveis**.

------------------------------------------------------------------------

# Visão Geral do Pipeline

Pipeline principal:

    Upload do artigo
          ↓
    Extração de texto
          ↓
    Mapeamento estrutural
          ↓
    Extração científica
          ↓
    Análise crítica
          ↓
    Verificação metodológica
          ↓
    Preparação para metanálise

Cada etapa gera **JSON estruturado reutilizável**.

------------------------------------------------------------------------

# Etapa 1 --- Visualizar Estrutura do Artigo

Objetivo:

Identificar seções principais do artigo.

Entrada:

    texto completo do artigo

Saída JSON:

``` json
{
  "title": "",
  "abstract": "",
  "sections": [
    "introduction",
    "methods",
    "results",
    "discussion"
  ],
  "tables_detected": [],
  "figures_detected": []
}
```

Prompt recomendado:

    You are a scientific document parser.

    Extract the structural sections of the article.

    Return ONLY JSON.

------------------------------------------------------------------------

# Etapa 2 --- Mapeamento Científico (PICO)

Objetivo:

Extrair a estrutura científica do estudo.

Saída JSON:

``` json
{
  "population": "",
  "intervention": "",
  "comparator": "",
  "outcomes": [],
  "study_design": ""
}
```

Prompt recomendado:

    Identify the PICO structure of the study.

    Return structured JSON only.

------------------------------------------------------------------------

# Etapa 3 --- Extração de Dados

Objetivo:

Extrair dados quantitativos para metanálise.

Saída JSON:

``` json
{
  "study_metadata": {
    "title": "",
    "authors": "",
    "year": null,
    "doi": ""
  },
  "population": {
    "total_sample_size": null,
    "intervention_group_n": null,
    "control_group_n": null
  },
  "outcomes": [
    {
      "name": "",
      "intervention_mean": null,
      "control_mean": null,
      "effect_type": ""
    }
  ]
}
```

Importante:

Este JSON será usado diretamente pela **metanálise**.

------------------------------------------------------------------------

# Etapa 4 --- Análise Crítica

Objetivo:

Avaliar qualidade metodológica do estudo.

Aspectos avaliados:

-   validade interna
-   risco de viés
-   limitações
-   aplicabilidade clínica

Saída:

    relatório crítico estruturado

------------------------------------------------------------------------

# Etapa 5 --- Avaliação de Risco de Viés

Ferramentas suportadas:

-   RoB2
-   ROBINS‑I

Saída JSON:

``` json
{
  "tool_used": "ROB2",
  "domains": {
    "randomization": "",
    "deviations": "",
    "missing_data": "",
    "measurement": "",
    "reporting": ""
  },
  "overall_risk": ""
}
```

------------------------------------------------------------------------

# Etapa 6 --- Preparação para Metanálise

Objetivo:

Normalizar dados para o módulo estatístico.

Saída JSON final:

``` json
{
  "study_id": "",
  "outcome": "",
  "n_intervention": null,
  "mean_intervention": null,
  "sd_intervention": null,
  "n_control": null,
  "mean_control": null,
  "sd_control": null
}
```

Este formato alimenta:

    meta_stats.py

------------------------------------------------------------------------

# Pipeline Interno no Backend

Fluxo:

    api.py
       ↓
    research_jobs.py
       ↓
    gpt_engine.py
       ↓
    analysis modules

Cada etapa grava resultados no banco.

------------------------------------------------------------------------

# Estrutura de Dados no Banco

Tabela:

    analysis_results

Campos:

    article_id
    structure_json
    pico_json
    data_extraction_json
    bias_json
    critical_analysis_text

------------------------------------------------------------------------

# Integração com Metanálise

Quando múltiplos estudos possuem o mesmo outcome:

    ≥ 3 estudos
    → sugerir metanálise

Fluxo:

    data_extraction_json
            ↓
    meta_stats.py
            ↓
    forest_plot

------------------------------------------------------------------------

# Benefícios desta Arquitetura

-   reuso de dados
-   prompts mais confiáveis
-   compatibilidade com metanálise
-   base para evidence graph

------------------------------------------------------------------------

# Futuro --- Evidence Graph

Cada estudo vira um nó:

    Study
     ├ Population
     ├ Intervention
     ├ Outcome
     └ Effect

Permite:

-   detectar evidência automaticamente
-   sugerir revisões sistemáticas
-   sugerir metanálises
