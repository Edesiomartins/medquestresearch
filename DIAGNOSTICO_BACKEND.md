# 🔧 Diagnóstico do Backend

## ⚡ Teste Rápido

### 1. Verificar se o Backend Está Rodando

**No PowerShell:**
```powershell
# Teste simples - deve retornar JSON
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
```

**Ou use o script de teste:**
```powershell
# Na raiz do projeto
.\test-backend.ps1
```

### 2. Se o Backend NÃO Está Rodando

**Passo 1: Navegue até a pasta backend**
```powershell
cd backend
```

**Passo 2: Instale as dependências (se necessário)**
```powershell
python -m pip install -r requirements.txt
```

**Passo 3: Inicie o servidor**
```powershell
python api.py
```

**Você deve ver:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Verificar Porta em Uso

Se a porta 8000 estiver ocupada:

```powershell
# Ver processos usando a porta 8000
netstat -ano | findstr :8000

# Matar processo (substitua PID pelo número)
taskkill /PID <PID> /F
```

### 4. Testar CORS Específico

**Teste OPTIONS (CORS preflight):**
```powershell
$headers = @{"Origin" = "http://localhost:3000"}
Invoke-WebRequest -Uri "http://localhost:8000/genapi/login" -Method OPTIONS -Headers $headers -UseBasicParsing
```

**Deve retornar status 200 ou 204 com headers CORS**

### 5. Verificar Logs do Backend

Quando você faz uma requisição, o terminal onde o backend está rodando deve mostrar logs como:

```
INFO:     127.0.0.1:XXXXX - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "OPTIONS /genapi/login HTTP/1.1" 200 OK
```

## 🐛 Problemas Comuns

### ❌ "Connection refused" ou "Não foi possível conectar"
- **Causa**: Backend não está rodando
- **Solução**: Inicie o backend com `python api.py` na pasta `backend/`

### ❌ "Port 8000 already in use"
- **Causa**: Outro processo está usando a porta
- **Solução**: Mate o processo ou use outra porta (configure `PORT=8001` no `.env`)

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
- **Causa**: Dependências não instaladas
- **Solução**: `python -m pip install -r backend/requirements.txt`

### ❌ CORS não funciona
- **Causa**: Backend não está respondendo corretamente às requisições OPTIONS
- **Solução**: Verifique se o `CORSMiddleware` está configurado corretamente no `api.py`

## ✅ Checklist

- [ ] Backend está rodando (`python api.py` executado)
- [ ] Porta 8000 está livre
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Rota `/` responde com status 200
- [ ] Rota `/ping` responde com status 200
- [ ] CORS OPTIONS funciona (`/genapi/login` com header Origin)

## 📞 Próximos Passos

Se todos os testes passarem mas o frontend ainda não conectar:

1. Verifique o `.env.local` do frontend:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

2. Reinicie o servidor Next.js após alterar `.env.local`

3. Verifique o console do navegador (F12) para erros específicos

4. Teste no navegador: http://localhost:8000/ deve mostrar JSON
