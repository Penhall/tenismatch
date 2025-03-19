#!/usr/bin/env python
"""
Script para executar testes de integração com PostgreSQL.
Este script configura o ambiente de teste e executa os testes de integração.

Uso:
    python scripts/run_postgres_tests.py [app_or_test]
"""

import os
import sys
import subprocess
from pathlib import Path

# Adiciona o diretório do projeto ao path do Python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def run_tests():
    """Executa os testes de integração com PostgreSQL."""
    print("=== Executando testes de integração com PostgreSQL ===")
    
    # Configura variáveis de ambiente para os testes
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.test_settings')
    
    # Obtém o teste ou app a ser executado
    test_to_run = sys.argv[1] if len(sys.argv) > 1 else 'apps.tenis_admin.test_transaction'
    
    # Executa os testes
    print(f"\nExecutando testes: {test_to_run}")
    try:
        # Usando o gerenciador de testes do Django
        result = subprocess.run(
            ["python", "manage.py", "test", test_to_run, "--keepdb", "-v", "2"],
            check=True,
            text=True
        )
        
        print("\n=== Testes concluídos com sucesso! ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n=== Falha na execução dos testes. Verifique os erros acima. ===")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
