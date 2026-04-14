# Manual do Usuário - MedquestResearch

## 1. Visão geral

O MedquestResearch é um webapp para apoiar revisões sistemáticas e metanálises científicas, com foco em:

- ingestão de artigos (PDF/DOCX);
- extração estruturada com revisão humana;
- análise quantitativa com múltiplos modelos;
- geração de visualizações (forest/funnel);
- redação científica por seções;
- exportação para submissão (DOCX e ZIP).

## 2. Acesso e navegação

- **Dashboard**: módulo principal para iniciar fluxos.
- **Metanálise** (`/meta-analise`): pipeline completo A -> H.
- **Manual** (`/manual`): guia de uso e chatbot de dúvidas.
- **Sidebar**: acesso a créditos, perfil, histórico de jobs e navegação.

## 3. Fluxo de metanálise

### Etapa A. Ingestão
- Envie múltiplos artigos em PDF/DOCX.
- Limite atual: até 25 arquivos por lote.
- O sistema inicia extração inicial dos estudos.

### Etapa B-C. Extração/Revisão
- Revise estudos e outcomes extraídos.
- Inclua/exclua estudos manualmente.
- Edite campos numéricos críticos:
  - contínuos: mean, sd, total (intervenção/comparador)
  - dicotômicos: events, total (intervenção/comparador)
- Use snippets e page hints para rastreabilidade.

### Etapa D-F. Modelagem/Pooling
- Defina pergunta da revisão.
- Escolha medida de efeito:
  - SMD (Hedges g)
  - log RR
  - log OR
- Escolha modelo:
  - fixed
  - random DL
  - random REML
  - random Paule-Mandel
- Se faltarem dados numéricos mínimos, o sistema pode cair para síntese narrativa.

### Etapa G-H. Síntese/Manuscrito
- Visualize:
  - resumo estatístico
  - tabela de efeitos
  - heterogeneidade
  - viés de publicação
  - subgrupos
  - sensibilidade leave-one-out
  - forest e funnel plot
- Gere texto científico por seções.

## 4. Exportações

### DOCX
- Exporta manuscrito consolidado com seções e resumo quantitativo.

### ZIP de submissão
Inclui:
- `README.txt`
- `manuscrito_meta_analise.docx`
- `meta_result_master.json`
- `effects_table.csv`
- `plots/forest_plot.svg`
- `plots/funnel_plot.svg`
- `narrative_results.txt`

## 5. Interpretação de warnings comuns

### "Pooling quantitativo indisponível por falta de dados completos"
Significa que os estudos estão incluídos, mas sem campos numéricos suficientes para o modelo selecionado.

Como corrigir:
1. Volte para B-C.
2. Complete os campos dos outcomes.
3. Para dados de eventos, prefira log RR/log OR.
4. Reexecute D-F.

## 6. Boas práticas de uso científico

- Sempre revisar manualmente as extrações.
- Registrar motivo de exclusão dos estudos.
- Não interpretar efeito combinado sem checar I², tau² e p de heterogeneidade.
- Usar viés de publicação e sensibilidade para qualificar conclusões.

## 7. Segurança e privacidade

- Não envie arquivos com dados sensíveis sem anonimização prévia.
- Use variáveis de ambiente seguras no deployment.
- Mantenha controle de acesso por token e perfil.

## 8. Suporte

Use o chatbot da página `/manual` para dúvidas operacionais e metodológicas.

