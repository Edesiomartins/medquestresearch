# 🔄 Novo Fluxo de Metanálise - PRISMA Check

## 📋 Mudanças Implementadas

### 1. Modelo Principal Atualizado
- **Modelo Principal**: `nvidia/nemotron-nano-12b-v2-vl` (GRATUITO)
- **Fallback**: `openai/gpt-4o-mini`, `openai/gpt-3.5-turbo`, `anthropic/claude-3-haiku`

### 2. Novo Fluxo da Metanálise

#### **ANTES (Fluxo Antigo):**
1. Usuário digita tema
2. Sistema busca artigos no PubMed automaticamente
3. Executa 4 etapas sequenciais

#### **AGORA (Novo Fluxo):**
1. **Upload de Artigos** (máximo 15 PDFs/DOCX)
2. **Análise PRISMA Automática** de cada artigo
3. **Geração de Escore** de qualidade (0-10)
4. **Exibição dos Resultados** com recomendações
5. **Usuário decide** se quer avançar para Fase 2
6. **Fases 2, 3 e 4** continuam normalmente

## 🔧 Endpoints Criados

### `/genapi/meta_analysis/upload_articles` (POST)
- Aceita múltiplos arquivos (máx 15)
- Processa cada PDF/DOCX
- Faz análise PRISMA automática
- Retorna escores e recomendações

**Resposta:**
```json
{
  "resultado": "Artigos processados e analisados com sucesso",
  "total_artigos": 5,
  "artigos": [
    {
      "arquivo": "artigo1.pdf",
      "titulo": "Título do Artigo",
      "texto_extraido": "...",
      "analise_prisma": {
        "tipo_estudo": "RCT",
        "escore_qualidade": 8,
        "pontuacao_prisma": 12,
        "risco_vies": "Baixo",
        "recomendacao": "Incluir",
        "pontos_fortes": [...],
        "pontos_fracos": [...]
      }
    }
  ],
  "resumo_analises": {
    "escore_medio": 7.5,
    "artigos_por_qualidade": {
      "excelente": 2,
      "boa": 2,
      "regular": 1,
      "baixa": 0
    }
  }
}
```

## 📊 Sistema de Escore PRISMA

### Critérios de Avaliação:
1. **Checklist PRISMA 2020** (14 itens)
2. **Risco de Viés** (RoB)
3. **Qualidade Metodológica**
4. **Tipo de Estudo**

### Escore de Qualidade (0-10):
- **9-10**: Excelente - Incluir automaticamente
- **7-8**: Boa - Incluir
- **5-6**: Regular - Incluir com ressalvas
- **<5**: Baixa - Excluir

### Recomendações:
- **Incluir**: Artigo de alta qualidade
- **Incluir com ressalvas**: Artigo aceitável mas com limitações
- **Excluir**: Artigo de baixa qualidade metodológica

## 🎯 Próximos Passos (Frontend)

1. **Criar componente de upload múltiplo**
   - Drag & drop para múltiplos arquivos
   - Preview dos arquivos selecionados
   - Limite de 15 arquivos

2. **Criar componente de exibição de escores**
   - Cards com análise PRISMA de cada artigo
   - Gráficos de distribuição de qualidade
   - Tabela com recomendações

3. **Modificar fluxo da metanálise**
   - Remover campo de tema (ou tornar opcional)
   - Adicionar upload múltiplo como primeira etapa
   - Exibir resultados PRISMA antes de avançar

4. **Integrar com etapas seguintes**
   - Passar artigos selecionados para Fase 2
   - Usar análises PRISMA nas etapas seguintes

## 📝 Configuração no Railway

### Variáveis de Ambiente:
```env
OPENAI_MODEL=nvidia/nemotron-nano-12b-v2-vl
OPENAI_MODEL_FALLBACK=openai/gpt-4o-mini,openai/gpt-3.5-turbo,anthropic/claude-3-haiku
```

## ⚠️ Notas Importantes

1. **Custo de Créditos**: 
   - Upload de PDF: 1 crédito por arquivo
   - Análise PRISMA: 1 crédito por artigo
   - Total: 2 créditos por artigo

2. **Limite de Arquivos**: Máximo 15 artigos por metanálise

3. **Tempo de Processamento**: 
   - Cada artigo leva ~30-60 segundos para análise PRISMA
   - 15 artigos podem levar 8-15 minutos

4. **Compatibilidade**: 
   - O fluxo antigo (busca no PubMed) ainda funciona como fallback
   - Se não houver artigos enviados, usa busca tradicional
