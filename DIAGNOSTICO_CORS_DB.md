# 🔧 Diagnóstico: CORS e Banco de Dados

## Problema Atual
- Erro: "Requisição cross-origin bloqueada: falha na requisição CORS"
- Código de status: (null)
- Suspeita: Banco de dados não está acessível

## 🔍 Testes Passo a Passo

### 1. Testar CORS Básico

**No navegador, abra:**
```
http://localhost:8000/cors-test
```

**Deve retornar:**
```json
{
  "status": "CORS Test",
  "message": "Se você vê esta mensagem, CORS está funcionando!",
  "timestamp": "..."
}
```

**Se funcionar:** CORS está OK ✅
**Se não funcionar:** Problema de CORS ❌

### 2. Testar Banco de Dados

**No navegador, abra:**
```
http://localhost:8000/genapi/test-db
```

**Deve retornar:**
```json
{
  "ok": true,
  "usuarios": <número>,
  "message": "Banco de dados está acessível!"
}
```

**Ou se não estiver configurado:**
```json
{
  "ok": false,
  "erro": "DATABASE_URL não configurada",
  "dica": "Configure a variável DATABASE_URL no ambiente"
}
```

### 3. Verificar Variáveis de Ambiente

**No terminal onde o backend está rodando, verifique:**

```powershell
# No PowerShell
$env:DATABASE_URL
```

**Ou crie um arquivo `.env` na pasta `backend/`:**

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database?sslmode=require
```

**Para desenvolvimento local com Railway:**
1. Acesse o Railway Dashboard
2. Vá em seu projeto → Variables
3. Copie o valor de `DATABASE_URL`
4. Cole no arquivo `.env` local

### 4. Testar Requisição OPTIONS (CORS Preflight)

**No PowerShell:**
```powershell
$headers = @{
    "Origin" = "http://localhost:3000"
    "Access-Control-Request-Method" = "POST"
    "Access-Control-Request-Headers" = "Content-Type,Authorization"
}
Invoke-WebRequest -Uri "http://localhost:8000/genapi/login" -Method OPTIONS -Headers $headers -UseBasicParsing
```

**Deve retornar status 200 ou 204 com headers CORS**

### 5. Verificar Logs do Backend

Quando você tenta fazer login, o terminal do backend deve mostrar:

```
INFO:     127.0.0.1:XXXXX - "OPTIONS /genapi/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "POST /genapi/login HTTP/1.1" 200 OK
```

**Se você NÃO vê a requisição OPTIONS:** O problema é CORS (requisição não está chegando)
**Se você vê OPTIONS mas não vê POST:** O problema pode ser validação de dados
**Se você vê POST mas dá erro:** O problema é banco de dados ou lógica

## 🐛 Soluções

### Problema: CORS não funciona

**Solução 1: Verificar se o backend está rodando**
```powershell
# Teste simples
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
```

**Solução 2: Reiniciar o backend**
```powershell
# Pare o backend (Ctrl+C)
# Inicie novamente
cd backend
python api.py
```

**Solução 3: Verificar firewall/antivírus**
- Alguns antivírus bloqueiam conexões locais
- Desative temporariamente para testar

### Problema: Banco de dados não acessível

**Solução 1: Configurar DATABASE_URL**
```powershell
# No PowerShell, antes de iniciar o backend:
$env:DATABASE_URL = "postgresql://usuario:senha@host:porta/database?sslmode=require"

# Ou crie arquivo backend/.env:
DATABASE_URL=postgresql://...
```

**Solução 2: Verificar conexão com Railway**
- Acesse Railway Dashboard
- Verifique se o banco está ativo
- Copie a DATABASE_URL correta

**Solução 3: Testar conexão manualmente**
```python
# Crie um arquivo test_db.py na pasta backend:
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL não configurada")
else:
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        print("✅ Conexão com banco de dados OK!")
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
```

## ✅ Checklist Final

- [ ] Backend está rodando (`python api.py`)
- [ ] Rota `/cors-test` funciona no navegador
- [ ] Rota `/genapi/test-db` mostra status do banco
- [ ] `DATABASE_URL` está configurada (se necessário)
- [ ] Requisição OPTIONS retorna status 200/204
- [ ] Logs do backend mostram requisições chegando
- [ ] Frontend está em `http://localhost:3000`
- [ ] Backend está em `http://localhost:8000`

## 📞 Próximos Passos

1. Execute os testes acima
2. Verifique qual teste falha
3. Siga a solução correspondente
4. Se ainda não funcionar, me informe qual teste falhou e qual erro apareceu
