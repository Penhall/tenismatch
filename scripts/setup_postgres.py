#!/usr/bin/env python
"""
Script para configurar o banco de dados PostgreSQL para o TenisMatch.
Este script cria o banco de dados, aplica as migrações e cria um superusuário.

Requisitos:
- PostgreSQL instalado e configurado
- Variáveis de ambiente configuradas no arquivo .env
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Adiciona o diretório do projeto ao path do Python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configura as variáveis de ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

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

def check_postgres():
    """Verifica se o PostgreSQL está instalado e acessível."""
    print("Verificando instalação do PostgreSQL...")
    return run_command("psql --version")

def create_database():
    """Cria o banco de dados PostgreSQL."""
    from django.conf import settings
    
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    
    print(f"Criando banco de dados '{db_name}'...")
    
    # Comando para criar o banco de dados
    create_db_command = f'psql -h {db_host} -p {db_port} -U {db_user} -c "CREATE DATABASE {db_name};"'
    
    # No Windows, pode ser necessário definir a senha como variável de ambiente
    if os.name == 'nt':  # Windows
        os.environ['PGPASSWORD'] = db_password
    
    return run_command(create_db_command)

def apply_migrations():
    """Aplica as migrações do Django."""
    print("Aplicando migrações...")
    return run_command("python manage.py migrate")

def create_superuser():
    """Cria um superusuário."""
    print("Criando superusuário...")
    
    # Importa o modelo de usuário
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Verifica se o superusuário já existe
    if User.objects.filter(username='Admin').exists():
        print("Superusuário 'Admin' já existe.")
        return True
    
    # Cria o superusuário
    try:
        User.objects.create_superuser(
            username='Admin',
            email='admin@grupo4.com',
            password='abc123',
            is_approved=True,
            role='GERENTE'
        )
        print("Superusuário 'Admin' criado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao criar superusuário: {e}")
        return False

def main():
    """Função principal."""
    print("=== Configuração do PostgreSQL para TenisMatch ===")
    
    # Verifica se o PostgreSQL está instalado
    if not check_postgres():
        print("PostgreSQL não encontrado. Por favor, instale o PostgreSQL e tente novamente.")
        return
    
    # Cria o banco de dados
    if not create_database():
        print("Falha ao criar o banco de dados. Verifique as credenciais e tente novamente.")
        return
    
    # Aplica as migrações
    if not apply_migrations():
        print("Falha ao aplicar as migrações. Verifique o log de erros e tente novamente.")
        return
    
    # Cria o superusuário
    if not create_superuser():
        print("Falha ao criar o superusuário. Verifique o log de erros e tente novamente.")
        return
    
    print("\n=== Configuração concluída com sucesso! ===")
    print("Banco de dados PostgreSQL configurado.")
    print("Migrações aplicadas.")
    print("Superusuário criado:")
    print("  Username: Admin")
    print("  Password: abc123")
    print("  Email: admin@grupo4.com")
    print("\nVocê pode iniciar o servidor com o comando:")
    print("  python manage.py runserver")

if __name__ == "__main__":
    main()
