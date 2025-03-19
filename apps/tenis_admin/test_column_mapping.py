"""
Testes unitários para o modelo ColumnMapping.
Este arquivo demonstra como escrever testes unitários usando pytest com PostgreSQL.
"""

import pytest
from django.contrib.auth import get_user_model
from .models import Dataset, ColumnMapping

User = get_user_model()

# Marca todos os testes como testes unitários e que requerem PostgreSQL
pytestmark = [pytest.mark.unit, pytest.mark.postgres]

@pytest.mark.django_db
class TestColumnMapping:
    """Testes para o modelo ColumnMapping."""
    
    def test_get_missing_mappings_all_missing(self):
        """Testa o método get_missing_mappings quando todas as colunas estão faltando."""
        # Criar usuário para o teste
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Criar dataset
        dataset = Dataset.objects.create(
            name='Test Dataset',
            description='Dataset para teste',
            uploaded_by=user,
            file='datasets/test.csv',
            records_count=100,
            is_processed=True,
            dataset_type='upload',
            file_size=1024,
            file_type='csv',
            status='ready'
        )
        
        # Criar mapeamento vazio
        mapping = ColumnMapping.objects.create(
            dataset=dataset,
            mapping={},
            is_validated=False
        )
        
        # Verificar se todas as colunas requeridas estão faltando
        missing = mapping.get_missing_mappings()
        assert len(missing) == 4
        assert 'tenis_marca' in missing
        assert 'tenis_estilo' in missing
        assert 'tenis_cores' in missing
        assert 'tenis_preco' in missing
    
    def test_get_missing_mappings_partial(self):
        """Testa o método get_missing_mappings quando algumas colunas estão mapeadas."""
        # Criar usuário para o teste
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        # Criar dataset
        dataset = Dataset.objects.create(
            name='Test Dataset 2',
            description='Dataset para teste',
            uploaded_by=user,
            file='datasets/test2.csv',
            records_count=100,
            is_processed=True,
            dataset_type='upload',
            file_size=1024,
            file_type='csv',
            status='ready'
        )
        
        # Criar mapeamento parcial
        mapping = ColumnMapping.objects.create(
            dataset=dataset,
            mapping={
                'col1': 'tenis_marca',
                'col2': 'tenis_estilo'
            },
            is_validated=False
        )
        
        # Verificar se apenas as colunas não mapeadas estão faltando
        missing = mapping.get_missing_mappings()
        assert len(missing) == 2
        assert 'tenis_cores' in missing
        assert 'tenis_preco' in missing
        assert 'tenis_marca' not in missing
        assert 'tenis_estilo' not in missing
    
    def test_get_missing_mappings_complete(self):
        """Testa o método get_missing_mappings quando todas as colunas estão mapeadas."""
        # Criar usuário para o teste
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='password123'
        )
        
        # Criar dataset
        dataset = Dataset.objects.create(
            name='Test Dataset 3',
            description='Dataset para teste',
            uploaded_by=user,
            file='datasets/test3.csv',
            records_count=100,
            is_processed=True,
            dataset_type='upload',
            file_size=1024,
            file_type='csv',
            status='ready'
        )
        
        # Criar mapeamento completo
        mapping = ColumnMapping.objects.create(
            dataset=dataset,
            mapping={
                'col1': 'tenis_marca',
                'col2': 'tenis_estilo',
                'col3': 'tenis_cores',
                'col4': 'tenis_preco'
            },
            is_validated=False
        )
        
        # Verificar se não há colunas faltando
        missing = mapping.get_missing_mappings()
        assert len(missing) == 0
