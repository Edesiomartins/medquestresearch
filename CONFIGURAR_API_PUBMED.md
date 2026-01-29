# 🔧 Configurar API do PubMed para Busca de Artigos

## 📋 Visão Geral

A plataforma agora utiliza a **API E-utilities do NCBI/PubMed** para buscar artigos científicos, com foco especial em **ensaios clínicos** e **estudos randomizados** para metanálises.

## ✅ Configuração Implementada

### 1. Variáveis de Ambiente

As seguintes variáveis foram adicionadas ao `backend/.env`:

```env
PUBMED_API_KEY=b15b1c39239c02cae32bd0164a66fcb54708
PUBMED_EMAIL=edesio.martins@unirv.edu.br
```

### 2. Funcionalidades Implementadas

- ✅ **Busca focada em ensaios clínicos**: A query automaticamente filtra por:
  - Clinical Trial
  - Randomized Controlled Trial
  - Controlled Clinical Trial
  - Meta-Analysis
  - Systematic Review

- ✅ **Extração de dados detalhados**: Para cada artigo encontrado, extrai:
  - PMID (PubMed ID)
  - Título
  - Autores (até 5 primeiros)
  - Ano de publicação
  - Abstract (resumo)
  - DOI (quando disponível)

- ✅ **Rate limiting**: Respeita os limites da API NCBI (3 requisições/segundo sem API key, 10/segundo com API key)

- ✅ **Tratamento de erros**: Tratamento robusto de timeouts e erros de conexão

## 🔧 Configuração no Railway

### Passo 1: Adicionar Variáveis de Ambiente

1. Acesse **Railway Dashboard** → Seu projeto → **Variables**
2. Adicione as seguintes variáveis:

```
PUBMED_API_KEY=b15b1c39239c02cae32bd0164a66fcb54708
PUBMED_EMAIL=edesio.martins@unirv.edu.br
```

### Passo 2: Fazer Redeploy

Após adicionar as variáveis, faça um **redeploy** do projeto para que as mudanças tenham efeito.

## 📊 Como Funciona

### Busca Automática na Metanálise

Quando o usuário inicia uma metanálise na **Etapa 1**:

1. O sistema recebe o tema da metanálise
2. Constrói uma query PubMed focada em ensaios clínicos:
   ```
   {tema} AND (Clinical Trial[ptyp] OR Randomized Controlled Trial[ptyp] OR ...)
   ```
3. Busca IDs dos artigos usando `esearch`
4. Busca detalhes completos usando `efetch`
5. Extrai informações estruturadas (título, autores, abstract, etc.)
6. Retorna os resultados para serem processados pela IA

### Exemplo de Resultado

```json
{
  "total": 150,
  "ids_encontrados": ["12345678", "12345679", ...],
  "artigos": [
    {
      "pmid": "12345678",
      "title": "Efficacy of Treatment X in Condition Y",
      "authors": ["Smith J", "Doe A", ...],
      "year": "2023",
      "abstract": "Background: ...",
      "doi": "10.1234/example"
    },
    ...
  ],
  "mensagem": "Encontrados 150 ensaios clínicos no PubMed",
  "query_usada": "{tema} AND (Clinical Trial[ptyp] OR ...)",
  "api_key_utilizada": "Sim"
}
```

## 🎯 Benefícios da API Key

**Sem API Key:**
- Limite: 3 requisições por segundo
- Pode causar delays em buscas grandes

**Com API Key:**
- Limite: 10 requisições por segundo
- Buscas mais rápidas
- Melhor experiência do usuário

## 🔍 Verificação

Para verificar se a API está funcionando:

1. Execute uma metanálise na plataforma
2. Na Etapa 1, verifique os logs do backend
3. Procure por mensagens como:
   ```
   Encontrados X ensaios clínicos no PubMed
   api_key_utilizada: Sim
   ```

## ⚠️ Notas Importantes

1. **Rate Limiting**: O código inclui um delay de 0.34 segundos entre requisições para respeitar os limites da API

2. **Limite de Artigos**: Por padrão, busca até 50 artigos, mas retorna detalhes completos de apenas 20 para evitar sobrecarga

3. **Filtros Automáticos**: A busca já filtra automaticamente por ensaios clínicos, então não é necessário adicionar filtros manuais na query

4. **Fallback**: Se a API do PubMed falhar, o sistema ainda pode usar a IA para gerar uma estratégia de busca baseada no tema

## 📚 Referências

- **NCBI E-utilities**: https://www.ncbi.nlm.nih.gov/books/NBK25497/
- **PubMed API**: https://www.ncbi.nlm.nih.gov/books/NBK25499/
- **Obter API Key**: https://www.ncbi.nlm.nih.gov/account/settings/

## 🐛 Troubleshooting

### Erro: "Timeout ao buscar no PubMed"
- **Causa**: Conexão lenta ou servidor NCBI sobrecarregado
- **Solução**: O sistema tentará novamente automaticamente

### Erro: "Nenhum ensaio clínico encontrado"
- **Causa**: Tema muito específico ou sem ensaios clínicos publicados
- **Solução**: Tente termos mais amplos ou verifique a query gerada nos logs

### API Key não está sendo usada
- **Verificação**: Confirme que `PUBMED_API_KEY` está configurada no Railway
- **Logs**: Verifique se `api_key_utilizada: Sim` aparece nos resultados
