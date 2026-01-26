# 🔧 Correção do Erro 402 - OpenRouter (Créditos Insuficientes)

## ⚠️ Problema

**Erro:** `Error code: 402 - This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 15322.`

**Causa:** A API do OpenRouter estava usando um valor padrão muito alto de `max_output_tokens` (65536), que excedia os créditos disponíveis na conta.

## ✅ Solução Implementada

### 1. **Adicionado parâmetro `max_output_tokens`**
- Valor padrão: **4000 tokens** (configurável via variável de ambiente)
- Limite máximo: **8000 tokens** (para evitar erros futuros)
- Configurável via: `OPENROUTER_MAX_OUTPUT_TOKENS`

### 2. **Modificações em `backend/gpt_engine.py`**

#### Função `_chamar_nova_api()` atualizada:
```python
def _chamar_nova_api(modelo, prompt, temperatura=None, max_output_tokens=None):
    # max_output_tokens padrão: 4000
    if max_output_tokens is None:
        max_output_tokens = int(os.getenv("OPENROUTER_MAX_OUTPUT_TOKENS", "4000"))
    
    # Limitar a 8000 tokens máximo
    max_output_tokens = min(max_output_tokens, 8000)
    
    params = {
        "model": modelo,
        "input": prompt,
        "max_output_tokens": max_output_tokens
    }
    
    if temperatura is not None:
        params["temperature"] = temperatura
    
    response = cliente.responses.create(**params)
    return response.output_text
```

#### Função `gerar_resposta()` atualizada:
- Agora aceita parâmetro opcional `max_output_tokens`
- Passa o parâmetro para `_chamar_nova_api()`

## 📋 Configuração

### Variável de Ambiente (Opcional)
```bash
OPENROUTER_MAX_OUTPUT_TOKENS=4000
```

**Valores recomendados:**
- **4000 tokens** - Padrão (seguro, evita erro 402)
- **6000 tokens** - Para respostas mais longas
- **8000 tokens** - Máximo recomendado

### Como Ajustar

1. **No Railway (Backend):**
   - Vá em **Variables**
   - Adicione: `OPENROUTER_MAX_OUTPUT_TOKENS=4000`
   - Faça redeploy

2. **Localmente (.env):**
   ```env
   OPENROUTER_MAX_OUTPUT_TOKENS=4000
   ```

## 🔍 Verificação

Após a correção, as requisições devem funcionar sem erro 402. O sistema agora:
- ✅ Usa `max_output_tokens=4000` por padrão
- ✅ Respeita o limite de créditos do OpenRouter
- ✅ Permite configuração via variável de ambiente
- ✅ Limita automaticamente a 8000 tokens máximo

## 📊 Impacto

- **Antes:** Erro 402 (créditos insuficientes) com 65536 tokens
- **Depois:** Funcionamento normal com 4000 tokens (suficiente para a maioria das respostas)

## ⚠️ Notas

1. **4000 tokens** é suficiente para a maioria das análises científicas
2. Se precisar de respostas mais longas, ajuste `OPENROUTER_MAX_OUTPUT_TOKENS`
3. O limite de 8000 tokens garante que não exceda os créditos disponíveis
4. Se ainda houver erro 402, verifique os créditos na conta OpenRouter

## 🚀 Próximos Passos

1. Fazer deploy das alterações
2. Testar uma requisição (ex: `/genapi/fatos`)
3. Verificar logs para confirmar que não há mais erro 402
4. Se necessário, ajustar `OPENROUTER_MAX_OUTPUT_TOKENS` conforme necessário
