from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import AIModel, Dataset, ModelMetrics
from .services import ModelTrainingService, ModelDeploymentService
import json

class IntegrationTests(TestCase):
    def setUp(self):
        # Criar grupos e usuários
        self.analyst_group = Group.objects.create(name='Analyst')
        self.manager_group = Group.objects.create(name='Manager')
        
        self.analyst = User.objects.create_user('analyst', 'analyst@test.com', 'password')
        self.manager = User.objects.create_user('manager', 'manager@test.com', 'password')
        
        self.analyst.groups.add(self.analyst_group)
        self.manager.groups.add(self.manager_group)
        
        self.client = Client()

    def test_complete_workflow(self):
        # 1. Login como analista
        self.client.login(username='analyst', password='password')
        
        # 2. Upload de dataset
        with open('test_data.csv', 'w') as f:
            f.write('col1,col2\n1,2\n3,4')
        
        with open('test_data.csv', 'rb') as f:
            response = self.client.post(reverse('admin:dataset_upload'), {
                'name': 'Test Dataset',
                'description': 'Test Description',
                'file': f
            })
        
        self.assertEqual(response.status_code, 302)
        dataset = Dataset.objects.first()
        
        # 3. Criar e treinar modelo
        response = self.client.post(reverse('admin:model_create'), {
            'name': 'Test Model',
            'version': '1.0',
            'dataset': dataset.id,
            'parameters': json.dumps({'n_factors': 100})
        })
        
        self.assertEqual(response.status_code, 302)
        model = AIModel.objects.first()
        
        # 4. Login como gerente para aprovação
        self.client.login(username='manager', password='password')
        
        response = self.client.post(reverse('admin:model_approve', args=[model.id]), {
            'action': 'approve',
            'review_notes': 'Approved'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 5. Verificar implantação
        model.refresh_from_db()
        self.assertEqual(model.status, 'approved')
        
        # 6. Testar métricas
        metrics = ModelMetrics.objects.create(
            model=model,
            accuracy=0.95,
            precision=0.94,
            recall=0.93,
            f1_score=0.94
        )
        
        response = self.client.get(reverse('admin:metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0.95')