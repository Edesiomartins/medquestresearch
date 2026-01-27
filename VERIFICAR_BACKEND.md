# 🔍 Verificar se o Backend Está Rodando

## ❌ Erro: NS_ERROR_CONNECTION_REFUSED

Este erro significa que **o backend não está rodando** ou não está escutando na porta 8000.

## ✅ Solução Passo a Passo

### 1. Verificar se o Backend Está Rodando

**Abra um terminal PowerShell e execute:**

```powershell
# Ver processos Python rodando
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# Ver se a porta 8000 está em uso
netstat -ano | findstr :8000
```

**Se não houver processos Python ou a porta 8000 não estiver em uso:** O backend não está rodando.

### 2. Iniciar o Backend

**No PowerShell:**

```powershell
# 1. Navegue até a pasta backend
cd backend

# 2. Verifique se está na pasta correta
ls api.py

# 3. Inicie o servidor
python api.py
```

**Você deve ver algo como:**

```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Verificar se Está Funcionando

**Em outro terminal PowerShell (mantenha o backend rodando):**

```powershell
# Teste simples
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing

# Ou use o script de teste
cd ..  # Volte para a raiz do projeto
.\test-backend.ps1
```

### 4. Testar no Navegador

**Depois que o backend estiver rodando, abra no navegador:**

- http://localhost:8000/
- http://localhost:8000/cors-test
- http://localhost:8000/genapi/test-db

**Todos devem retornar JSON.**

## 🐛 Problemas Comuns

### Problema: "python: command not found"

**Solução:**
```powershell
# Use python3 ou py
py api.py
# ou
python3 api.py
```

### Problema: "ModuleNotFoundError"

**Solução:**
```powershell
# Instale as dependências
python -m pip install -r requirements.txt
```

### Problema: "Port 8000 already in use"

**Solução:**
```powershell
# Encontre o processo
netstat -ano | findstr :8000

# Mate o processo (substitua PID)
taskkill /PID <PID> /F

# Ou use outra porta
$env:PORT=8001
python api.py
```

### Problema: Backend inicia mas não responde

**Verifique:**
1. Não há erros no terminal onde o backend está rodando
2. O firewall não está bloqueando a porta 8000
3. Você está usando `http://localhost:8000` (não `https://`)

## ✅ Checklist

- [ ] Backend está rodando (`python api.py` executado)
- [ ] Terminal mostra "Uvicorn running on http://0.0.0.0:8000"
- [ ] Porta 8000 está em uso (`netstat -ano | findstr :8000`)
- [ ] `http://localhost:8000/` retorna JSON no navegador
- [ ] Não há erros no terminal do backend

## 📝 Próximos Passos

1. **Certifique-se de que o backend está rodando**
2. **Mantenha o terminal do backend aberto** (não feche)
3. **Teste no navegador:** http://localhost:8000/
4. **Se funcionar, teste:** http://localhost:8000/cors-test
5. **Depois teste o frontend novamente**
