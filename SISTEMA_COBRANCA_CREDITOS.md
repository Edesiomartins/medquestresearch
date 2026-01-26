# 💳 Sistema de Cobrança de Créditos - MedQuestResearch

## 📋 Visão Geral

O sistema de cobrança de créditos foi implementado para gerenciar o uso de recursos da plataforma. Cada tipo de requisição possui um custo em créditos que é debitado automaticamente antes do processamento.

## 🏗️ Arquitetura

### Módulo Central: `backend/credit_costs.py`

Este módulo centraliza todos os custos e permite configuração via variáveis de ambiente.

### Função Principal: `get_credit_cost(modulo: str) -> int`

Retorna o custo em créditos para um módulo específico, priorizando variáveis de ambiente sobre valores padrão.

## 💰 Custos Padrão

| Módulo | Custo (Créditos) | Descrição |
|--------|------------------|-----------|
| `explicar` / `explain_concept` | **5** | Explicar conceito científico |
| `critica` / `critical_analysis` | **7** | Análise crítica de artigo |
| `fatos` / `fact_checker` | **5** | Verificação de fatos |
| `perspectiva` / `perspective_research` | **10** | Pesquisa de perspectivas (usa API externa) |
| `mapa` / `structure_visualizer` | **8** | Mapa conceitual / Visualização de estrutura |
| `structure_mapper` | **6** | Mapeador de estrutura |
| `meta_analise` / `meta_analysis` | **12** | Meta-análise completa (mais complexo) |
| `pdf` | **3** | Upload e processamento de PDF/DOCX |

## ⚙️ Configuração via Variáveis de Ambiente

### Formato

```bash
CREDIT_COST_<MODULO_UPPERCASE>=<valor>
```

### Exemplos

```bash
# Ajustar custo de explicação de conceitos
CREDIT_COST_EXPLICAR=6

# Ajustar custo de meta-análise
CREDIT_COST_META_ANALISE=15

# Ajustar custo de verificação de fatos
CREDIT_COST_FATOS=4
```

### Configuração no Railway

1. Acesse o projeto no Railway
2. Vá em **Variables**
3. Adicione as variáveis no formato:
   ```
   CREDIT_COST_<MODULO>=<valor>
   ```
4. Faça redeploy

### Configuração Local (.env)

```env
# Custos personalizados
CREDIT_COST_EXPLICAR=6
CREDIT_COST_CRITICA=8
CREDIT_COST_META_ANALISE=15
```

## 🔄 Fluxo de Cobrança

1. **Usuário faz requisição** → Rota da API é chamada
2. **Sistema obtém custo** → `get_credit_cost("modulo")`
3. **Verifica créditos disponíveis** → `debitar_creditos(usuario_id, custo)`
4. **Se insuficiente** → Retorna erro `402 Payment Required`
5. **Se suficiente** → Debita créditos e processa requisição
6. **Registra no log** → Salva custo no `research_jobs` e `gen_logs_uso`

## 📊 Funções Disponíveis

### `get_credit_cost(modulo: str) -> int`

Obtém o custo de um módulo específico.

```python
from backend.credit_costs import get_credit_cost

custo = get_credit_cost("explicar")  # Retorna 5 (ou valor configurado)
```

### `get_all_costs() -> Dict[str, int]`

Retorna todos os custos configurados (incluindo variáveis de ambiente).

```python
from backend.credit_costs import get_all_costs

custos = get_all_costs()
# Retorna: {"explicar": 5, "critica": 7, ...}
```

### `set_credit_cost(modulo: str, custo: int) -> None`

Define o custo de um módulo (apenas em memória, para testes).

```python
from backend.credit_costs import set_credit_cost

set_credit_cost("explicar", 6)  # Ajusta temporariamente
```

## 🔐 Rotas de API

### Rotas Administrativas

#### `GET /genapi/admin/custos`

Lista todos os custos configurados (requer autenticação).

**Resposta:**
```json
{
  "custos": {
    "explicar": 5,
    "critica": 7,
    "fatos": 5,
    "perspectiva": 10,
    "mapa": 8,
    "structure_mapper": 6,
    "meta_analise": 12,
    "pdf": 3
  },
  "total_modulos": 8,
  "observacao": "Valores podem ser ajustados via variáveis de ambiente CREDIT_COST_<MODULO>"
}
```

### Todas as rotas de análise cobram créditos automaticamente:

- `POST /genapi/explain_concept` → 5 créditos
- `POST /genapi/critical_analysis` → 7 créditos
- `POST /genapi/fact_checker` → 5 créditos
- `POST /genapi/perspective_research` → 10 créditos
- `POST /genapi/structure_visualizer` → 8 créditos
- `POST /genapi/structure_mapper` → 6 créditos
- `POST /genapi/meta_analysis` → 12 créditos
- `POST /genapi/pdf` → 3 créditos

### Resposta de Erro (Créditos Insuficientes)

```json
{
  "detail": "Créditos insuficientes"
}
```

**Status Code:** `402 Payment Required`

## 📝 Exemplo de Uso nas Rotas

```python
from backend.credit_costs import get_credit_cost

@api_router.post("/explicar")
def rota_explicar(request: Request, data: InputTexto, user = Depends(require_api_key)):
    # Obter custo do módulo
    custo = get_credit_cost("explicar")
    
    # Verificar e debitar créditos
    if not debitar_creditos(user["id"], custo):
        raise HTTPException(status_code=402, detail="Créditos insuficientes")
    
    # Processar requisição...
```

## 🎯 Ajustando Valores

### Método 1: Variáveis de Ambiente (Recomendado)

Ajuste os valores via variáveis de ambiente no Railway ou `.env`:

```bash
CREDIT_COST_EXPLICAR=6
CREDIT_COST_CRITICA=8
CREDIT_COST_META_ANALISE=15
```

### Método 2: Editar `credit_costs.py`

Edite diretamente o arquivo `backend/credit_costs.py`:

```python
DEFAULT_COSTS: Dict[str, int] = {
    "explicar": 6,  # Ajustado de 5 para 6
    "critica": 8,    # Ajustado de 7 para 8
    # ...
}
```

## 📈 Monitoramento

### Verificar Créditos do Usuário

```bash
GET /genapi/creditos
Authorization: Bearer <token>
```

**Resposta:**
```json
{
  "creditos": 100,
  "creditos_usados": 25,
  "creditos_disponiveis": 75
}
```

### Verificar Logs de Uso

Os custos são registrados em:
- `research_jobs.creditos` - Custo da requisição
- `gen_logs_uso.creditos_gastos` - Histórico de uso

## ⚠️ Observações Importantes

1. **Créditos são debitados ANTES do processamento** - Se o processamento falhar, os créditos não são reembolsados automaticamente
2. **Valores devem ser inteiros positivos** - Valores negativos ou zero causarão erro
3. **Variáveis de ambiente têm prioridade** - Se `CREDIT_COST_EXPLICAR=6` estiver definido, sobrescreve o valor padrão
4. **Módulos não configurados** - Se um módulo não tiver custo configurado, levantará `ValueError`

## 🔧 Troubleshooting

### Erro: "Módulo 'xyz' não possui custo configurado"

**Solução:** Adicione o módulo em `DEFAULT_COSTS` em `credit_costs.py`:

```python
DEFAULT_COSTS: Dict[str, int] = {
    # ...
    "xyz": 5,  # Adicionar novo módulo
}
```

### Erro: "Créditos insuficientes" mesmo com créditos disponíveis

**Verificar:**
1. Se `creditos - creditos_usados >= custo`
2. Se o valor do custo não foi alterado recentemente
3. Se há outras requisições simultâneas consumindo créditos

### Valores não estão sendo aplicados

**Verificar:**
1. Se a variável de ambiente está no formato correto: `CREDIT_COST_<MODULO_UPPERCASE>`
2. Se o servidor foi reiniciado após alterar variáveis de ambiente
3. Se não há erros de sintaxe no valor (deve ser número inteiro)

## 🚀 Próximos Passos

1. **Definir valores finais** - Ajustar custos conforme análise de custos reais
2. **Implementar reembolso** - Adicionar lógica de reembolso em caso de falha
3. **Dashboard de custos** - Criar interface para visualizar e ajustar custos
4. **Histórico detalhado** - Melhorar logs para análise de uso
