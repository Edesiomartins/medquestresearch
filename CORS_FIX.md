# 🔧 Correção de CORS - Railway

## ❌ Problema

Erro de CORS ao fazer requisições do frontend para o backend:
```
CORS Missing Allow Origin
Requisição cross-origin bloqueada
```

## ✅ Solução Implementada

O código do backend foi atualizado para incluir automaticamente:
- `https://medquestresearch.up.railway.app` (frontend Railway)
- `http://localhost:3000` (desenvolvimento local)
- `http://localhost:3001` (desenvolvimento local alternativo)

## 🔧 Configuração no Railway

### Opção 1: Usar Defaults (Recomendado)

O backend já inclui as URLs principais por padrão. **Não é necessário** configurar `ALLOWED_ORIGINS` se você estiver usando:
- Frontend em `medquestresearch.up.railway.app`

### Opção 2: Configurar Manualmente

Se precisar adicionar URLs adicionais, configure no Railway:

1. No painel do Railway (backend), vá em **Variables**
2. Adicione a variável:
   ```
   ALLOWED_ORIGINS=https://medquestresearch.up.railway.app,https://outra-url.com
   ```
3. Separe múltiplas URLs por vírgula (sem espaços)

## 🔍 Verificação

Após fazer commit e push:

1. O Railway fará redeploy automaticamente
2. Teste uma requisição do frontend
3. O erro de CORS deve desaparecer

## 📝 URLs Incluídas por Padrão

- ✅ `https://medquestresearch.up.railway.app`
- ✅ `http://localhost:3000` (dev)
- ✅ `http://localhost:3001` (dev alternativo)

## ⚠️ Importante

- As URLs são combinadas (defaults + variável de ambiente)
- Não há duplicatas (usando `set()`)
- URLs devem incluir o protocolo (`https://` ou `http://`)
