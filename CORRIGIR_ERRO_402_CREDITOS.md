# 🔧 Corrigir Erro 402 - Créditos Insuficientes

## 📋 Problema

O erro **402** indica que a conta OpenRouter não tem créditos suficientes para gerar a quantidade de tokens solicitada.

**Mensagem de erro:**
```
Error code: 402 - This request requires more credits, or fewer max_tokens. 
You requested up to 4000 tokens, but can only afford 30.
```

## ✅ Solução Implementada

O código foi atualizado para:

1. **Reduzir o padrão de `max_output_tokens`** de 4000 para **1000 tokens**
2. **Detectar automaticamente erro 402** e reduzir `max_output_tokens` pela metade
3. **Tentar novamente** com tokens reduzidos antes de passar para o próximo modelo

## 🔧 Configuração no Railway

### Opção 1: Configurar Variável de Ambiente (Recomendado)

1. Acesse **Railway Dashboard** → Seu projeto → **Variables**
2. Adicione/edite a variável:
   ```
   OPENROUTER_MAX_OUTPUT_TOKENS=500
   ```
   (Use um valor baixo como 200-500 se tiver poucos créditos)

3. Faça **redeploy** do projeto

### Opção 2: Adicionar Créditos na Conta OpenRouter

1. Acesse https://openrouter.ai/settings/credits
2. Adicione créditos à sua conta
3. Aumente `OPENROUTER_MAX_OUTPUT_TOKENS` para um valor maior (ex: 2000)

## 📊 Valores Recomendados

| Créditos Disponíveis | `OPENROUTER_MAX_OUTPUT_TOKENS` |
|----------------------|--------------------------------|
| Muito baixos (< 100) | 50-100 |
| Baixos (100-500)     | 200-500 |
| Médios (500-2000)    | 1000-1500 |
| Altos (> 2000)       | 2000 |

## 🧪 Teste

Após configurar, teste executando uma análise:

1. O sistema tentará com o valor configurado
2. Se receber erro 402, reduzirá automaticamente pela metade
3. Tentará novamente com tokens reduzidos
4. Se ainda falhar, tentará modelos de fallback

## 📝 Logs

Os logs mostrarão:
```
[GPT_ENGINE] Tentando modelo 1/4: 'openai/gpt-5-mini' (max_tokens=1000)
[GPT_ENGINE] ⚠️ Erro 402 detectado! Reduzindo max_output_tokens para 500
[GPT_ENGINE] ✅ Sucesso após reduzir tokens para 500
```

## ⚠️ Importante

- O sistema **reduz automaticamente** os tokens quando detecta erro 402
- O valor mínimo é **50 tokens** (não reduz abaixo disso)
- Se todos os modelos falharem mesmo com tokens reduzidos, você precisa **adicionar créditos** na conta OpenRouter
