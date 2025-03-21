from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import AIModel, Dataset, ModelMetrics
from .services import ModelTrainingService, ModelDeploymentService
import json
import tempfile
import os

class IntegrationTests(TransactionTestCase):
    databases = '__all__'  # Usa todos os bancos de dados configurados
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Verificar conexão com PostgreSQL
        from django.db import connections
        connection = connections['default']
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Conectado ao PostgreSQL: {version[0]}")
    
    def setUp(self):
        # Criar grupos e usuários
        self.analyst_group = Group.objects.create(name='Analyst')
        self.manager_group = Group.objects.create(name='Manager')
        
        self.analyst = User.objects.create_user('analyst', 'analyst@test.com', 'password')
        self.manager = User.objects.create_user('manager', 'manager@test.com', 'password')
        
        self.analyst.groups.add(self.analyst_group)
        self.manager.groups.add(self.manager_group)
        
        self.client = Client()
        
        # Criar arquivo temporário para testes
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.temp_file.write(b'col1,col2\n1,2\n3,4')
        self.temp_file.close()

    def tearDown(self):
        # Limpar arquivo temporário
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_complete_workflow(self):
        # 1. Login como analista
        self.client.login(username='analyst', password='password')
        
        # 2. Upload de dataset
        with open(self.temp_file.name, 'rb') as f:
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
