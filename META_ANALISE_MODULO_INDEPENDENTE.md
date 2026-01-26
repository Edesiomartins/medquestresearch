# 📑 Módulo de Meta-Análise - Implementação Completa

## ✅ Alterações Realizadas

### 1. **Backend - Busca na Literatura** (`backend/literature_search.py`)
- ✅ Função `buscar_literatura()` que busca em PubMed, LILACS e Cochrane
- ✅ `_buscar_pubmed()` - Busca real na API do PubMed (E-utilities)
- ✅ `_buscar_lilacs()` - Busca na API do LILACS (BVS)
- ✅ `_buscar_cochrane()` - Gera estratégia de busca (API não pública)
- ✅ Função `gerar_resumo_busca()` para resumir resultados

### 2. **Backend - Meta-Análise Modificada** (`backend/meta_analysis.py`)
- ✅ Função `gerar_meta_analise()` agora recebe `tema` como parâmetro principal
- ✅ `texto_artigo` é opcional (usado apenas nas etapas 2-4)
- ✅ Nova função `_criar_prompt_etapa1_com_busca()` que:
  - Realiza busca automática na literatura
  - Gera pergunta PICO
  - Cria estratégia de busca
  - Estabelece protocolo de seleção

### 3. **Backend - API Atualizada** (`backend/api.py`)
- ✅ `InputMetaAnalise` modificado: `tema` é obrigatório, `texto_artigo` é opcional
- ✅ `processar_job_meta_analise()` atualizado para receber tema primeiro
- ✅ Rota `/genapi/meta_analise` atualizada

### 4. **Frontend - Página Dedicada** (`frontend/app/meta-analise/page.tsx`)
- ✅ Página completa e independente para meta-análise
- ✅ Formulário para inserir tema da revisão
- ✅ Botões para executar etapas individualmente ou todas sequencialmente
- ✅ Cards informativos sobre cada etapa
- ✅ Integração com sistema de janelas de resultados

### 5. **Frontend - API Atualizada** (`frontend/app/lib/api.ts`)
- ✅ Interface `MetaAnaliseParams` atualizada: `tema` obrigatório
- ✅ Função `metaAnalysis()` atualizada

### 6. **Frontend - Página Principal** (`frontend/app/page.tsx`)
- ✅ Removido ToolCard de meta-análise (não precisa mais de artigo)
- ✅ Adicionado card informativo com link para página de meta-análise
- ✅ Removidas referências ao modal de meta-análise

### 7. **Frontend - Sidebar** (`frontend/app/components/ui/sidebar.tsx`)
- ✅ Adicionado link "Meta-Análise PRISMA" na navegação

## 🔄 Fluxo do Módulo de Meta-Análise

### Etapa 1: Estruturação PICO + Busca na Literatura
1. Usuário insere o **tema** da revisão
2. Sistema realiza buscas automáticas em:
   - **PubMed** (via API E-utilities)
   - **LILACS** (via API BVS)
   - **Cochrane** (estratégia de busca gerada)
3. Sistema gera:
   - Pergunta PICO estruturada
   - Estratégia de busca detalhada (MeSH/DeCS)
   - Critérios de inclusão/exclusão
   - Protocolo de seleção

### Etapa 2: Extração de Dados
- Usuário fornece artigos selecionados (PDFs ou texto)
- Sistema extrai dados em formato JSON estruturado
- Cria tabela de evidências

### Etapa 3: Redação Técnica (PRISMA)
- Redige seções: Métodos, Resultados, Discussão
- Conforme protocolo PRISMA 2020
- Suporta estilos Vancouver e ABNT

### Etapa 4: Verificação Final
- Revisão de conformidade PRISMA
- Verificação de dados
- Formatação final

## 🚀 Como Usar

1. **Acessar o módulo:**
   - Via sidebar: clicar em "Meta-Análise PRISMA"
   - Via dashboard: clicar no card "Meta-Análise PRISMA"

2. **Inserir tema:**
   - Digite o tema da revisão sistemática
   - Exemplo: "Eficácia da intervenção X em pacientes com condição Y"

3. **Executar:**
   - **Opção 1:** Executar apenas Etapa 1 (PICO + Busca)
   - **Opção 2:** Executar todas as etapas sequencialmente

4. **Acompanhar resultados:**
   - Cada etapa abre uma janela de resultado
   - Resultados podem ser visualizados e copiados

## 📋 Bases de Dados Suportadas

- ✅ **PubMed** - Busca real via API E-utilities
- ✅ **LILACS** - Busca via API BVS (Biblioteca Virtual em Saúde)
- ✅ **Cochrane** - Estratégia de busca gerada (API requer acesso institucional)

## ⚠️ Observações Importantes

1. **Etapa 1 não requer artigo:** A busca é feita automaticamente com base no tema
2. **Etapas 2-4 podem requerer artigos:** Dependendo do que foi gerado na Etapa 1
3. **Busca na literatura:** Pode levar alguns minutos, especialmente no PubMed
4. **Rate limiting:** Implementado para respeitar limites das APIs

## 🔧 Dependências

- `requests` - Para chamadas HTTP às APIs de busca (já no requirements.txt)

## 📝 Próximos Passos (Opcional)

- [ ] Adicionar cache de buscas para evitar repetições
- [ ] Melhorar parsing de resultados do PubMed
- [ ] Adicionar suporte a mais bases de dados
- [ ] Implementar download de artigos encontrados
- [ ] Adicionar filtros avançados de busca
