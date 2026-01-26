#!/usr/bin/env python3
"""
Script para adicionar créditos a um usuário via linha de comando.
Uso: python adicionar_creditos.py <email_ou_id> <quantidade>
"""

import sys
import os

# Adicionar o diretório ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from database import db_select_one, db_execute, get_connection
except ImportError:
    try:
        import backend.database as database
        db_select_one = database.db_select_one
        db_execute = database.db_execute
        get_connection = database.get_connection
    except ImportError:
        print("❌ Erro: Não foi possível importar o módulo database")
        sys.exit(1)

def adicionar_creditos(identificador: str, quantidade: int):
    """Adiciona créditos a um usuário identificado por email ou ID."""
    try:
        # Tentar como ID primeiro
        try:
            usuario_id = int(identificador)
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE id = %s", (usuario_id,))
        except ValueError:
            # Se não for número, tratar como email
            usuario = db_select_one("SELECT id, nome, email, creditos FROM usuarios WHERE email = %s", (identificador,))

        if not usuario:
            print(f"❌ Usuário não encontrado: {identificador}")
            return False

        creditos_anteriores = usuario["creditos"]
        
        # Adicionar créditos
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET creditos = creditos + %s WHERE id = %s",
                    (quantidade, usuario["id"])
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    # Buscar dados atualizados
                    usuario_atualizado = db_select_one(
                        "SELECT id, nome, email, creditos, creditos_usados FROM usuarios WHERE id = %s",
                        (usuario["id"],)
                    )
                    
                    print(f"✅ Créditos adicionados com sucesso!")
                    print(f"   Usuário: {usuario_atualizado['nome']} ({usuario_atualizado['email']})")
                    print(f"   Créditos anteriores: {creditos_anteriores}")
                    print(f"   Créditos adicionados: {quantidade}")
                    print(f"   Créditos atuais: {usuario_atualizado['creditos']}")
                    print(f"   Créditos usados: {usuario_atualizado.get('creditos_usados', 0)}")
                    print(f"   Créditos disponíveis: {usuario_atualizado['creditos'] - usuario_atualizado.get('creditos_usados', 0)}")
                    return True
                else:
                    print(f"❌ Erro: Nenhuma linha foi atualizada")
                    return False
        finally:
            conn.close()

    except Exception as e:
        print(f"❌ Erro ao adicionar créditos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python adicionar_creditos.py <email_ou_id> <quantidade>")
        print("\nExemplos:")
        print("  python adicionar_creditos.py usuario@email.com 100")
        print("  python adicionar_creditos.py 1 50")
        sys.exit(1)

    identificador = sys.argv[1]
    try:
        quantidade = int(sys.argv[2])
    except ValueError:
        print(f"❌ Erro: Quantidade deve ser um número inteiro")
        sys.exit(1)

    if quantidade <= 0:
        print(f"❌ Erro: Quantidade deve ser maior que zero")
        sys.exit(1)

    sucesso = adicionar_creditos(identificador, quantidade)
    sys.exit(0 if sucesso else 1)
