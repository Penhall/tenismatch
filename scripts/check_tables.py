import os
import sys
import django

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar as conexões do Django
from django.db import connection

# Verificar tabelas existentes
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print("Tabelas existentes no banco de dados:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Verificar especificamente as tabelas users e auth_user
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        );
    """)
    users_exists = cursor.fetchone()[0]
    print(f"\nTabela 'users' existe: {users_exists}")
    
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'auth_user'
        );
    """)
    auth_user_exists = cursor.fetchone()[0]
    print(f"Tabela 'auth_user' existe: {auth_user_exists}")
