#!/usr/bin/env python
"""
Script para criar as migrações do Django para o TenisMatch.
"""

import os
import sys
import subprocess
from pathlib import Path

# Adiciona o diretório do projeto ao path do Python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def run_command(command):
    """Executa um comando e retorna o resultado."""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False

def create_migrations():
    """Cria as migrações do Django."""
    print("Criando migrações para apps.users...")
    run_command("python manage.py makemigrations users")
    
    print("Criando migrações para apps.profiles...")
    run_command("python manage.py makemigrations profiles")
    
    print("Criando migrações para apps.matching...")
    run_command("python manage.py makemigrations matching")
    
    print("Criando migrações para apps.tenis_admin...")
    run_command("python manage.py makemigrations tenis_admin")
    
    print("Criando migrações para todas as aplicações...")
    run_command("python manage.py makemigrations")

def main():
    """Função principal."""
    print("=== Criando migrações para o TenisMatch ===")
    
    create_migrations()
    
    print("\n=== Migrações criadas com sucesso! ===")
    print("\nPara aplicar as migrações, execute:")
    print("  python manage.py migrate")
    print("\nPara criar um superusuário, execute:")
    print("  python manage.py createsuperuser")

if __name__ == "__main__":
    main()
