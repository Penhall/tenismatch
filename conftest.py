"""
Configurações e fixtures para o pytest.
Este arquivo é carregado automaticamente pelo pytest e contém configurações e fixtures
que serão usadas em todos os testes.
"""

import os
import pytest
import tempfile
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client

# Marca todos os testes que usam o banco de dados
pytestmark = pytest.mark.django_db

# Configurações para o pytest
def pytest_configure(config):
    """Configurações para o pytest."""
    # Verifica se o PostgreSQL está configurado
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
        pytest.skip("Testes requerem PostgreSQL")
    
    # Configura o diretório temporário para arquivos de mídia
    settings.MEDIA_ROOT = tempfile.mkdtemp()

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configuração do banco de dados para os testes."""
    with django_db_blocker.unblock():
        # Verifica a conexão com o PostgreSQL
        from django.db import connections
        connection = connections['default']
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Conectado ao PostgreSQL: {version[0]}")

@pytest.fixture
def analyst_user():
    """Fixture que cria um usuário analista."""
    analyst_group, _ = Group.objects.get_or_create(name='Analyst')
    user = User.objects.create_user(
        username='analyst_test',
        email='analyst_test@example.com',
        password='password123'
    )
    user.groups.add(analyst_group)
    return user

@pytest.fixture
def manager_user():
    """Fixture que cria um usuário gerente."""
    manager_group, _ = Group.objects.get_or_create(name='Manager')
    user = User.objects.create_user(
        username='manager_test',
        email='manager_test@example.com',
        password='password123'
    )
    user.groups.add(manager_group)
    return user

@pytest.fixture
def analyst_client(analyst_user):
    """Fixture que cria um cliente autenticado como analista."""
    client = Client()
    client.login(username='analyst_test', password='password123')
    return client

@pytest.fixture
def manager_client(manager_user):
    """Fixture que cria um cliente autenticado como gerente."""
    client = Client()
    client.login(username='manager_test', password='password123')
    return client

@pytest.fixture
def temp_csv_file():
    """Fixture que cria um arquivo CSV temporário."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_file.write(b'col1,col2\n1,2\n3,4')
    temp_file.close()
    yield temp_file.name
    # Limpa o arquivo após o teste
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)
