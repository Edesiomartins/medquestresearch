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

## 3. Fluxo de metanálise (detalhado por situação)

### Etapa A. Ingestão
- Objetivo: carregar os artigos que serão triados e extraídos.
- Ação do usuário: enviar arquivos PDF/DOCX (até 25 por lote).
- Resultado esperado: criação de um `project_id` e lista inicial de estudos detectados.

Situações comuns:
- **Upload bem-sucedido**: você avança para B-C com estudos listados.
- **Formato inválido**: aparece erro indicando arquivo não suportado.
- **Arquivo grande**: arquivos muito grandes podem ser recusados para proteger desempenho.

### Etapa B-C. Extração/Revisão
- Objetivo: revisar manualmente a extração e preparar dados para pooling.
- Ação do usuário:
  - incluir/excluir estudos;
  - registrar motivo de exclusão;
  - ajustar outcomes e números (mean/sd/events/totals);
  - usar snippets/page hints para conferência.

Situações comuns:
- **Estudo incluído sem dados numéricos completos**: o sistema mantém a inclusão, mas gera nota de limitação para pooling.
- **Exclusão manual sem motivo**: o sistema sugere motivo padrão.
- **Dados conflitantes**: recomenda-se revisar o PDF e corrigir manualmente os campos.

### Etapa D-F. Modelagem/Pooling
- Objetivo: executar a metanálise quantitativa e análises complementares.
- Ação do usuário:
  - definir pergunta da revisão;
  - escolher medida de efeito;
  - escolher modelo estatístico.

Interpretação da escolha de medida:
- **SMD (Hedges g)**: para desfechos contínuos com média/desvio padrão.
- **log RR**: para desfechos dicotômicos baseados em risco.
- **log OR**: para desfechos dicotômicos baseados em odds/chances.

Interpretação da escolha de modelo:
- **fixed**: assume efeito verdadeiro comum entre estudos.
- **random DL**: efeitos aleatórios com DerSimonian-Laird.
- **random REML**: efeitos aleatórios com estimativa REML de heterogeneidade.
- **random PM**: efeitos aleatórios com Paule-Mandel.

Situações comuns:
- **Pooling quantitativo disponível**: gera efeito combinado, IC95%, p global, heterogeneidade e plots.
- **Pooling quantitativo indisponível**: ocorre quando faltam dados numéricos mínimos em estudos suficientes; o sistema retorna síntese narrativa e warning.
- **Erro de configuração**: pode acontecer se menos de 2 estudos estiverem incluídos.

### Etapa G-H. Síntese/Manuscrito
- Objetivo: transformar resultados em saída científica utilizável.
- Entregas exibidas:
  - resumo estatístico;
  - tabela de efeitos;
  - heterogeneidade (Q, I², tau², p heterogeneidade);
  - viés de publicação (Egger/Begg);
  - subgrupos;
  - sensibilidade leave-one-out;
  - forest plot e funnel plot;
  - texto científico por seções (resumo, introdução, métodos, resultados, discussão, conclusão).

Situações comuns:
- **Warning metodológico**: indica limitação de dados, sem necessariamente ser erro técnico.
- **Exportação concluída**: DOCX e ZIP ficam disponíveis para submissão/auditoria.
- **Necessidade de ajuste**: você pode clicar nas etapas do topo para voltar e corrigir.

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
O histórico do chat é persistido por usuário autenticado e pode ser limpo pelo botão "Limpar".

