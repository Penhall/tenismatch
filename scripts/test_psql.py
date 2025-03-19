#!/usr/bin/env python
"""
Script para testar a conexão com o banco de dados PostgreSQL usando subprocess.
"""

import subprocess
import sys

def test_psql():
    """Testa a conexão com o banco de dados PostgreSQL usando psql."""
    print("Testando conexão com o PostgreSQL usando psql...")
    
    try:
        # Definir variáveis de ambiente
        env = {
            'PGUSER': 'postgres',
            'PGPASSWORD': 'abc123',
            'PGHOST': 'localhost',
            'PGPORT': '5432',
            'PGDATABASE': 'tenismatch'
        }
        
        # Executar comando psql
        cmd = ['psql', '-c', 'SELECT version();']
        
        # Executar o comando
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Mostrar resultado
        print("Conexão estabelecida com sucesso!")
        print(result.stdout)
        
        # Testar tabelas criadas
        print("\nVerificando tabelas criadas:")
        cmd = ['psql', '-c', "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"]
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # Testar usuário Admin
        print("\nVerificando usuário Admin:")
        cmd = ['psql', '-c', "SELECT id, username, email, is_superuser FROM users WHERE username = 'Admin';"]
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar psql: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False
    
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_psql()
    sys.exit(0 if success else 1)
