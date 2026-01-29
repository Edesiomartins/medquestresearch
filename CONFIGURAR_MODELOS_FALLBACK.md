# 🔄 Sistema de Fallback de Modelos

## ✅ Implementado!

Agora você pode configurar **múltiplos modelos** no OpenRouter. Se o modelo principal falhar, o sistema tenta automaticamente os modelos de fallback.

## 📝 Como Configurar

### No Railway Dashboard → Variables:

**1. Modelo Principal (obrigatório):**
```
OPENAI_MODEL=openai/gpt-5-mini
```

**2. Modelos de Fallback (opcional):**
```
OPENAI_MODEL_FALLBACK=openai/gpt-4o-mini,openai/gpt-3.5-turbo
```

### Exemplo Completo:

```
OPENAI_MODEL=openai/gpt-5-mini
OPENAI_MODEL_FALLBACK=openai/gpt-4o-mini,openai/gpt-3.5-turbo,anthropic/claude-3-haiku
```

## 🔄 Como Funciona

1. **Primeira tentativa:** Usa `OPENAI_MODEL` (modelo principal)
2. **Se falhar:** Tenta automaticamente o primeiro modelo de `OPENAI_MODEL_FALLBACK`
3. **Se falhar novamente:** Tenta o próximo modelo da lista
4. **Continua até:** Um modelo funcionar ou todos falharem

## 💡 Vantagens

- ✅ **Maior confiabilidade:** Se um modelo estiver indisponível, usa outro automaticamente
- ✅ **Economia:** Pode usar modelos mais baratos como fallback
- ✅ **Flexibilidade:** Escolha modelos diferentes para diferentes necessidades

## 📋 Modelos Recomendados

### Para Qualidade (ordem de preferência):
```
OPENAI_MODEL=openai/gpt-5-mini
OPENAI_MODEL_FALLBACK=openai/gpt-4o,anthropic/claude-3.5-sonnet
```

### Para Economia (ordem de preferência):
```
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_MODEL_FALLBACK=openai/gpt-3.5-turbo,anthropic/claude-3-haiku
```

### Para Velocidade:
```
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_MODEL_FALLBACK=openai/gpt-3.5-turbo
```

## ⚠️ Importante

- Use o formato completo: `openai/gpt-5-mini` (não apenas `gpt-5-mini`)
- Separe múltiplos modelos por vírgula: `modelo1,modelo2,modelo3`
- Sem espaços extras entre modelos
- O sistema tenta em ordem (primeiro o principal, depois os fallbacks)

## 📊 Logs

O sistema registra qual modelo foi usado:
- `✅ Modelo principal funcionou` - Usou o modelo principal
- `✅ Modelo funcionou (fallback)` - Usou um modelo de fallback
- `⚠️ Modelo falhou, tentando próximo...` - Tentando próximo modelo
- `❌ Todos os modelos falharam` - Nenhum modelo funcionou
