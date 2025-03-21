# /tenismatch/apps/tenis_admin/tests.py 
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import AIModel, Dataset

User = get_user_model()

class TenisAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Criar grupos
        self.analyst_group = Group.objects.create(name='Analyst')
        self.manager_group = Group.objects.create(name='Manager')
        
        # Criar usuários
        self.analyst = User.objects.create_user(
            username='analyst',
            password='testpass123',
            email='analyst@test.com'
        )
        self.manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            email='manager@test.com'
        )
        
        self.analyst.groups.add(self.analyst_group)
        self.manager.groups.add(self.manager_group)

    def test_analyst_access(self):
        self.client.login(username='analyst', password='testpass123')
        
        response = self.client.get(reverse('tenis_admin:analyst_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('tenis_admin:manager_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_dataset_upload(self):
        self.client.login(username='analyst', password='testpass123')
        
        test_file = SimpleUploadedFile(
            "test.csv",
            b"col1,col2\n1,2\n3,4",
            content_type="text/csv"
        )
        
        response = self.client.post(reverse('tenis_admin:dataset_upload'), {
            'name': 'Test Dataset',
            'description': 'Test Description',
            'file': test_file
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Dataset.objects.exists())

    def test_model_workflow(self):
        self.client.login(username='analyst', password='testpass123')
        
        # Criar modelo
        model = AIModel.objects.create(
            name='Test Model',
            version='1.0',
            description='Test Description',
            created_by=self.analyst,
            status='review'
        )
        
        # Manager aprova modelo
        self.client.login(username='manager', password='testpass123')
        response = self.client.post(
            reverse('tenis_admin:model_approve', args=[model.id]),
            {'decision': 'approved', 'review_notes': 'Approved'}
        )
        
        model.refresh_from_db()
        self.assertEqual(model.status, 'approved')