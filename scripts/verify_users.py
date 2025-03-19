#!/usr/bin/env python
"""
Script para verificar os usuários criados no banco de dados PostgreSQL.
"""
import os
import sys
import django

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def verify_users():
    """
    Verifica os usuários criados no banco de dados.
    """
    usernames = ['tester', 'Analyst', 'Manager']
    
    print("Verificando usuários no banco de dados PostgreSQL...")
    print("-" * 60)
    print(f"{'Username':<15} {'Email':<25} {'Perfil':<15} {'Aprovado':<10}")
    print("-" * 60)
    
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            role_display = user.get_role_display() if user.role else 'Comum'
            print(f"{user.username:<15} {user.email:<25} {role_display:<15} {'Sim' if user.is_approved else 'Não':<10}")
        except User.DoesNotExist:
            print(f"{username:<15} {'NÃO ENCONTRADO':<25} {'-':<15} {'-':<10}")
    
    print("-" * 60)

if __name__ == '__main__':
    verify_users()
