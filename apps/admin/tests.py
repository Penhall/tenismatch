# /tenismatch/apps/admin/tests.py 
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import AIModel, Dataset, ModelMetrics

class AdminTests(TestCase):
    def setUp(self):
        # Criar grupos
        self.analyst_group = Group.objects.create(name='Analyst')
        self.manager_group = Group.objects.create(name='Manager')
        
        # Criar usuários
        self.analyst = User.objects.create_user('analyst', 'analyst@test.com', 'password')
        self.manager = User.objects.create_user('manager', 'manager@test.com', 'password')
        
        self.analyst.groups.add(self.analyst_group)
        self.manager.groups.add(self.manager_group)
        
        self.client = Client()

    def test_analyst_access(self):
        self.client.login(username='analyst', password='password')
        response = self.client.get(reverse('admin:analyst_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:manager_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_manager_access(self):
        self.client.login(username='manager', password='password')
        response = self.client.get(reverse('admin:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:analyst_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_model_approval_flow(self):
        self.client.login(username='analyst', password='password')
        
        # Criar modelo
        model_data = {
            'name': 'Test Model',
            'version': '1.0',
            'description': 'Test Description'
        }
        response = self.client.post(reverse('admin:model_training'), model_data)
        self.assertEqual(response.status_code, 302)
        
        model = AIModel.objects.first()
        self.assertEqual(model.status, 'draft')
        
        # Manager aprova modelo
        self.client.login(username='manager', password='password')
        response = self.client.post(
            reverse('admin:model_approve', args=[model.id]),
            {'action': 'approve', 'review_notes': 'Approved'}
        )
        
        model.refresh_from_db()
        self.assertEqual(model.status, 'approved')