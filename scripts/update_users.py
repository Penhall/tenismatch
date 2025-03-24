# /tenismatch/scripts/update_users.py

import os
import sys
import django

# Configure Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.models import User
import logging

logger = logging.getLogger(__name__)

def update_user_roles():
    """
    Script para atualizar usuários regulares que foram erroneamente classificados como Analistas.
    """
    # Lista de usuários que devem continuar como Analistas (coloque os usernames aqui)
    keep_as_analyst = ['analyst']  # exemplo: mantém o usuário 'analyst' como analista
    
    # Lista de usuários que devem continuar como Gerentes (coloque os usernames aqui)
    keep_as_manager = ['manager']  # exemplo: mantém o usuário 'manager' como gerente
    
    # Obter todos os usuários com papel ANALISTA
    analyst_users = User.objects.filter(role='ANALISTA')
    count = 0
    
    print(f"Encontrados {analyst_users.count()} usuários com papel ANALISTA")
    
    for user in analyst_users:
        # Verificar se o usuário deve permanecer como Analista
        if user.username in keep_as_analyst:
            print(f"Mantendo {user.username} como ANALISTA (na lista de exceções)")
            continue
        
        # Verificar se é um superusuário
        if user.is_superuser:
            print(f"Mantendo {user.username} como ANALISTA (é superusuário)")
            continue
        
        # Mudar para usuário regular
        user.role = 'USUARIO'
        user.save()
        count += 1
        print(f"Usuário {user.username} alterado para USUARIO")
    
    # Verificar se há usuários GERENTE que deveriam ser USUARIO
    manager_users = User.objects.filter(role='GERENTE')
    
    print(f"Encontrados {manager_users.count()} usuários com papel GERENTE")
    
    for user in manager_users:
        # Verificar se o usuário deve permanecer como Gerente
        if user.username in keep_as_manager:
            print(f"Mantendo {user.username} como GERENTE (na lista de exceções)")
            continue
        
        # Verificar se é um superusuário
        if user.is_superuser:
            print(f"Mantendo {user.username} como GERENTE (é superusuário)")
            continue
        
        # Mudar para usuário regular
        user.role = 'USUARIO'
        user.save()
        count += 1
        print(f"Usuário {user.username} alterado para USUARIO")
    
    return count

if __name__ == "__main__":
    print("======= ATUALIZADOR DE PAPÉIS DE USUÁRIO =======")
    print("Este script atualiza usuários regulares que foram erroneamente classificados como Analistas.")
    choice = input("\nDeseja continuar? (s/n): ")
    
    if choice.lower() == 's':
        count = update_user_roles()
        print(f"\n{count} usuários foram atualizados para o papel USUARIO.")
        print("Operação concluída com sucesso.")
    else:
        print("\nOperação cancelada.")