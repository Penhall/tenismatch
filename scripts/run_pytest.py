#!/usr/bin/env python
"""
Script para executar testes com pytest.
Este script configura o ambiente de teste e executa os testes usando pytest.

Uso:
    python scripts/run_pytest.py [args]
    
Exemplos:
    python scripts/run_pytest.py                           # Executa todos os testes
    python scripts/run_pytest.py apps/tenis_admin          # Executa testes do módulo tenis_admin
    python scripts/run_pytest.py -v -m integration         # Executa testes de integração com verbose
    python scripts/run_pytest.py -v -m "not integration"   # Executa testes que não são de integração
"""

import os
import sys
import subprocess
from pathlib import Path

# Adiciona o diretório do projeto ao path do Python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def run_pytest():
    """Executa os testes usando pytest."""
    print("=== Executando testes com pytest ===")
    
    # Configura variáveis de ambiente para os testes
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.test_settings')
    
    # Verifica se o pytest está instalado
    try:
        import pytest
    except ImportError:
        print("Pytest não está instalado. Instalando...")
        subprocess.run(["pip", "install", "pytest", "pytest-django", "pytest-xdist"], check=True)
    
    # Verifica a conexão com o PostgreSQL
    try:
        print("Verificando conexão com PostgreSQL...")
        import psycopg2
        conn_string = "dbname='test_tenismatch' user='postgres' password='abc123' host='localhost' port='5432'"
        
        # Tenta conectar ao banco de dados de teste
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Conexão estabelecida com sucesso ao banco de dados de teste!")
            print(f"Versão do PostgreSQL: {version[0]}")
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            # Se o banco de dados de teste não existir, tenta criar
            print("Banco de dados de teste não encontrado. Tentando criar...")
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='abc123',
                host='localhost',
                port='5432'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE test_tenismatch;")
            print("Banco de dados de teste criado com sucesso!")
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        print("Verifique se o PostgreSQL está em execução e se as credenciais estão corretas.")
        return False
    
    # Executa os testes
    print("\nExecutando testes com pytest...")
    
    # Obtém argumentos da linha de comando
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Adiciona argumentos padrão se não houver argumentos específicos
    if not args:
        args = ["apps/tenis_admin/test_integration_pytest.py", "-v"]
    
    # Adiciona argumentos para reutilizar o banco de dados
    if "--reuse-db" not in args and "-k" not in args:
        args.append("--reuse-db")
    
    # Executa o pytest
    try:
        result = subprocess.run(
            ["pytest"] + args,
            check=True,
            text=True
        )
        print("\n=== Testes concluídos com sucesso! ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n=== Falha na execução dos testes. Verifique os erros acima. ===")
        return False

if __name__ == "__main__":
    success = run_pytest()
    sys.exit(0 if success else 1)
