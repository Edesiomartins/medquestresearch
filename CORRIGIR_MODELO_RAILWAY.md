# 🔧 Corrigir Modelo no Railway

## ⚠️ Problema Identificado

No Railway, a variável `OPENAI_MODEL` está configurada como:
```
gpt-5-mini
```

Mas o OpenRouter requer o formato completo:
```
openai/gpt-5-mini
```

## ✅ Solução

### No Railway Dashboard:

1. Acesse: https://railway.app
2. Selecione seu projeto **MedquestResearch**
3. Vá em **Variables**
4. Encontre a variável `OPENAI_MODEL`
5. Clique nos três pontos (⋯) → **Edit**
6. Altere o valor de:
   ```
   gpt-5-mini
   ```
   Para:
   ```
   openai/gpt-5-mini
   ```
7. Clique em **Save**

### Alternativa: Usar GPT-4o Mini (Mais Barato)

Se preferir um modelo mais barato, use:
```
openai/gpt-4o-mini
```

## 📝 Modelos Disponíveis no OpenRouter

- `openai/gpt-5-mini` - GPT-5 Mini (mais rápido, mais barato que GPT-5)
- `openai/gpt-4o-mini` - GPT-4o Mini (mais barato ainda)
- `openai/gpt-4o` - GPT-4o (mais poderoso)
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet

## ✅ Após Corrigir

1. O Railway vai fazer redeploy automaticamente
2. Aguarde alguns segundos
3. Teste a metanálise novamente

O erro deve desaparecer após essa correção!
