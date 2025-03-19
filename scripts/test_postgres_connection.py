#!/usr/bin/env python
"""
Script para testar a conexão com o banco de dados PostgreSQL.
"""

import psycopg2
import sys

def test_connection():
    """Testa a conexão com o banco de dados PostgreSQL."""
    print("Testando conexão com o PostgreSQL...")
    
    try:
        # String de conexão direta
        conn_string = "dbname='tenismatch' user='postgres' password='abc123' host='localhost' port='5432'"
        
        # Conectar ao banco de dados
        conn = psycopg2.connect(conn_string)
        
        # Criar um cursor
        cursor = conn.cursor()
        
        # Executar uma consulta simples
        cursor.execute("SELECT version();")
        
        # Obter o resultado
        version = cursor.fetchone()
        print(f"Conexão estabelecida com sucesso!")
        print(f"Versão do PostgreSQL: {version[0]}")
        
        # Testar tabelas criadas
        print("\nVerificando tabelas criadas:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
        
        # Testar usuário Admin
        print("\nVerificando usuário Admin:")
        cursor.execute("SELECT id, username, email, is_superuser FROM users WHERE username = 'Admin';")
        admin = cursor.fetchone()
        
        if admin:
            print(f"Usuário Admin encontrado:")
            print(f"- ID: {admin[0]}")
            print(f"- Username: {admin[1]}")
            print(f"- Email: {admin[2]}")
            print(f"- Is Superuser: {admin[3]}")
        else:
            print("Usuário Admin não encontrado.")
        
        # Fechar cursor e conexão
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
