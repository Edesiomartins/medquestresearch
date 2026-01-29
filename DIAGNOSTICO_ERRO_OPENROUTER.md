# 🔍 Diagnóstico: Erro OpenRouter API

## ❌ Erro Atual

O traceback está cortado, mas o erro ocorre em:
```
cliente.responses.create(**params)
```

## 🔧 Possíveis Causas

### 1. Modelo Incorreto
**Problema:** O modelo pode estar sem o prefixo correto.

**Solução:** No Railway → Variables, verifique:
```
OPENAI_MODEL=openai/gpt-5-mini  ✅ Correto
OPENAI_MODEL=gpt-5-mini          ❌ Incorreto (falta prefixo)
```

### 2. Modelo Não Disponível
**Problema:** O modelo `openai/gpt-5-mini` pode não estar disponível ou requer chave própria da OpenAI.

**Solução:** Tente usar um modelo mais comum:
```
OPENAI_MODEL=openai/gpt-4o-mini
```

### 3. Créditos Insuficientes
**Problema:** A conta OpenRouter pode estar sem créditos.

**Solução:**
1. Acesse: https://openrouter.ai/settings/credits
2. Verifique o saldo
3. Adicione créditos se necessário

### 4. Chave de API Inválida
**Problema:** A chave pode estar incorreta ou expirada.

**Solução:**
1. Verifique a chave em: https://openrouter.ai/keys
2. Gere uma nova chave se necessário
3. Atualize no Railway → Variables

### 5. Headers Faltando
**Problema:** OpenRouter pode exigir headers específicos.

**Solução:** Adicione no Railway → Variables:
```
OPENROUTER_REFERRER=https://medquestresearch.up.railway.app
OPENROUTER_TITLE=MedQuestResearch
```

## ✅ Solução Rápida

### Passo 1: Verificar Modelo

No Railway → Variables, certifique-se de que:
```
OPENAI_MODEL=openai/gpt-4o-mini
```

(Não use `gpt-5-mini` sem o prefixo `openai/`)

### Passo 2: Adicionar Modelos de Fallback

Adicione fallbacks no Railway → Variables:
```
OPENAI_MODEL_FALLBACK=openai/gpt-3.5-turbo,anthropic/claude-3-haiku
```

### Passo 3: Verificar Créditos

1. Acesse: https://openrouter.ai/settings/credits
2. Verifique se há créditos disponíveis

### Passo 4: Verificar Logs

Após fazer deploy, verifique os logs do Railway para ver:
- Qual modelo está sendo usado
- Qual é a mensagem de erro completa
- Status code do erro

## 📋 Checklist

- [ ] `OPENAI_MODEL` está no formato correto (`openai/gpt-4o-mini`)
- [ ] `OPENAI_API_BASE` está configurado (`https://openrouter.ai/api/v1`)
- [ ] `API_OPENAI_KEY_RESEARCH` está correta
- [ ] Há créditos na conta OpenRouter
- [ ] Headers OpenRouter configurados (opcional)

## 🔍 Próximos Passos

1. **Verifique os logs completos no Railway** para ver a mensagem de erro completa
2. **Teste com um modelo mais simples:** `openai/gpt-3.5-turbo`
3. **Verifique créditos** na conta OpenRouter
4. **Teste a chave** diretamente na API do OpenRouter

## 💡 Modelos Recomendados para Teste

**Mais Barato e Confiável:**
```
OPENAI_MODEL=openai/gpt-3.5-turbo
```

**Bom Custo-Benefício:**
```
OPENAI_MODEL=openai/gpt-4o-mini
```

**Mais Poderoso (mais caro):**
```
OPENAI_MODEL=openai/gpt-4o
```
