#!/usr/bin/env python3
"""
Script simples para testar se o servidor está respondendo
"""
import requests
import sys

def test_server(base_url="http://localhost:8000"):
    """Testa se o servidor está respondendo"""
    print(f"🔍 Testando servidor em: {base_url}")
    print("-" * 50)
    
    # Teste 1: Rota raiz
    try:
        print("1. Testando rota raiz (/)...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Resposta: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERRO: Não foi possível conectar ao servidor!")
        print(f"   💡 Certifique-se de que o backend está rodando:")
        print(f"      cd backend")
        print(f"      python api.py")
        return False
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False
    
    # Teste 2: Rota ping
    try:
        print("\n2. Testando rota /ping...")
        response = requests.get(f"{base_url}/ping", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Resposta: {response.json()}")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False
    
    # Teste 3: CORS - OPTIONS request
    try:
        print("\n3. Testando CORS (OPTIONS)...")
        response = requests.options(
            f"{base_url}/genapi/login",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        print(f"   ✅ Status: {response.status_code}")
        cors_origin = response.headers.get("Access-Control-Allow-Origin", "NÃO ENCONTRADO")
        print(f"   📄 CORS Origin: {cors_origin}")
        if cors_origin == "*" or "localhost" in cors_origin:
            print("   ✅ CORS configurado corretamente!")
        else:
            print("   ⚠️ CORS pode não estar funcionando corretamente")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram! O servidor está funcionando.")
    return True

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = test_server(base_url)
    sys.exit(0 if success else 1)
