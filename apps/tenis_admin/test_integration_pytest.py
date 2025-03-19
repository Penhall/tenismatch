"""
Testes de integração usando pytest para o módulo tenis_admin.
Este arquivo demonstra como escrever testes de integração usando pytest com PostgreSQL.
"""

import pytest
import json
from django.urls import reverse
from .models import AIModel, Dataset, ModelMetrics

# Marca todos os testes como testes de integração e que requerem PostgreSQL
pytestmark = [pytest.mark.integration, pytest.mark.postgres]

@pytest.mark.django_db(transaction=True)
class TestIntegrationWithPytest:
    """Testes de integração usando pytest."""
    
    def test_complete_workflow(self, analyst_client, manager_client, temp_csv_file):
        """Testa o fluxo completo do sistema."""
        # 1. Upload de dataset como analista
        with open(temp_csv_file, 'rb') as f:
            response = analyst_client.post(reverse('admin:dataset_upload'), {
                'name': 'Test Dataset Pytest',
                'description': 'Test Description Pytest',
                'file': f
            })
        
        assert response.status_code == 302
        dataset = Dataset.objects.first()
        assert dataset is not None
        assert dataset.name == 'Test Dataset Pytest'
        
        # 2. Criar e treinar modelo
        response = analyst_client.post(reverse('admin:model_create'), {
            'name': 'Test Model Pytest',
            'version': '1.0',
            'dataset': dataset.id,
            'parameters': json.dumps({'n_factors': 100})
        })
        
        assert response.status_code == 302
        model = AIModel.objects.first()
        assert model is not None
        assert model.name == 'Test Model Pytest'
        
        # 3. Aprovação do modelo pelo gerente
        response = manager_client.post(reverse('admin:model_approve', args=[model.id]), {
            'action': 'approve',
            'review_notes': 'Approved via pytest'
        })
        
        assert response.status_code == 302
        
        # 4. Verificar implantação
        model.refresh_from_db()
        assert model.status == 'approved'
        
        # 5. Testar métricas
        metrics = ModelMetrics.objects.create(
            model=model,
            accuracy=0.96,
            precision=0.95,
            recall=0.94,
            f1_score=0.95
        )
        
        response = manager_client.get(reverse('admin:metrics'))
        assert response.status_code == 200
        assert b'0.96' in response.content

    def test_analyst_permissions(self, analyst_client, manager_client):
        """Testa as permissões de analista e gerente."""
        # Analista pode acessar dashboard de analista
        response = analyst_client.get(reverse('admin:analyst_dashboard'))
        assert response.status_code == 200
        
        # Analista não pode acessar dashboard de gerente
        response = analyst_client.get(reverse('admin:manager_dashboard'))
        assert response.status_code == 403
        
        # Gerente pode acessar dashboard de gerente
        response = manager_client.get(reverse('admin:manager_dashboard'))
        assert response.status_code == 200
