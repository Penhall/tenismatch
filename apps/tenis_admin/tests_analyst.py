from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Dataset, AIModel
import pandas as pd
import io

class AnalystFunctionalityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuração inicial para todos os testes
        cls.client = Client()
        cls.valid_csv = SimpleUploadedFile(
            "test_dataset.csv",
            b"col1,col2\n1,2\n3,4",
            content_type="text/csv"
        )
        cls.invalid_csv = SimpleUploadedFile(
            "bad_dataset.csv",
            b"invalid,data",
            content_type="text/csv"
        )

    def test_dataset_upload(self):
        """Testa o upload de um dataset válido"""
        response = self.client.post(
            reverse('dataset-upload'),
            {'file': self.valid_csv, 'name': 'Test Dataset'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Dataset.objects.filter(name='Test Dataset').exists())

    def test_dataset_naming(self):
        """Verifica se o nome do dataset é salvo corretamente"""
        response = self.client.post(
            reverse('dataset-upload'),
            {'file': self.valid_csv, 'name': 'Named Dataset'},
            follow=True
        )
        dataset = Dataset.objects.first()
        self.assertEqual(dataset.name, 'Named Dataset')

    def test_invalid_dataset_upload(self):
        """Testa o upload de um dataset inválido"""
        response = self.client.post(
            reverse('dataset-upload'),
            {'file': self.invalid_csv, 'name': 'Bad Dataset'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Dataset.objects.filter(name='Bad Dataset').exists())

    def test_model_initialization(self):
        """Testa a inicialização de um modelo com dataset"""
        # Cria um dataset de teste
        dataset = Dataset.objects.create(
            name='Test Dataset',
            file=self.valid_csv
        )
        
        # Testa a criação do modelo
        response = self.client.post(
            reverse('model-create'),
            {
                'name': 'Test Model',
                'dataset': dataset.id,
                'model_type': 'linear_regression'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        model = AIModel.objects.first()
        self.assertEqual(model.name, 'Test Model')
        self.assertEqual(model.dataset.id, dataset.id)

    def test_model_training(self):
        """Testa o processo de treinamento de um modelo"""
        # Cria dataset e modelo
        dataset = Dataset.objects.create(
            name='Training Dataset',
            file=self.valid_csv
        )
        model = AIModel.objects.create(
            name='Training Model',
            dataset=dataset,
            model_type='linear_regression'
        )
        
        # Inicia o treinamento
        response = self.client.post(
            reverse('model-train', args=[model.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        model.refresh_from_db()
        self.assertIsNotNone(model.training_completed_at)
        self.assertEqual(model.status, 'completed')
