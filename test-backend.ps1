# Script PowerShell para testar o backend
# Execute: .\test-backend.ps1

Write-Host "🔍 Testando Backend MedQuestResearch" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

# Teste 1: Rota raiz
Write-Host "`n1. Testando rota raiz (/)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   📄 Resposta: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ ERRO: Não foi possível conectar ao servidor!" -ForegroundColor Red
    Write-Host "   💡 Certifique-se de que o backend está rodando:" -ForegroundColor Yellow
    Write-Host "      cd backend" -ForegroundColor White
    Write-Host "      python api.py" -ForegroundColor White
    exit 1
}

# Teste 2: Rota ping
Write-Host "`n2. Testando rota /ping..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/ping" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   📄 Resposta: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ ERRO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Teste 3: CORS - OPTIONS request
Write-Host "`n3. Testando CORS (OPTIONS)..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = "http://localhost:3000"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/genapi/login" -Method OPTIONS -Headers $headers -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $corsOrigin = $response.Headers["Access-Control-Allow-Origin"]
    if ($corsOrigin) {
        Write-Host "   📄 CORS Origin: $corsOrigin" -ForegroundColor Gray
        if ($corsOrigin -eq "*" -or $corsOrigin -like "*localhost*") {
            Write-Host "   ✅ CORS configurado corretamente!" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ CORS pode não estar funcionando corretamente" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️ Header CORS não encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ ERRO: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 Isso pode ser normal se o servidor não suportar OPTIONS" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ Testes concluídos!" -ForegroundColor Green
Write-Host "`nSe todos os testes passaram, o backend está funcionando corretamente." -ForegroundColor Cyan
