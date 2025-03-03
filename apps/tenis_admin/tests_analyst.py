from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.tenis_admin.services import (
    DataProcessor,
    DatasetService,
    ModelTrainingService,
    MetricsService,
    ModelDeploymentService
)
from apps.tenis_admin.models import Dataset, AIModel

class AnalystAreaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuração inicial para todos os testes
        cls.dataset = Dataset.objects.create(
            file="media/datasets/synthetic_dataset_20250226214423.csv",
            description="Dataset de teste",
            is_active=True
        )
        cls.model = AIModel.objects.create(
            name="Modelo Teste",
            version="1.0",
            is_active=True
        )

    def test_data_processing_flow(self):
        """Testa todo o fluxo de processamento de dados"""
        processor = DataProcessor(self.dataset)
        
        # Teste de carregamento de dados
        data = processor.load_data()
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)
        
        # Teste de limpeza de dados
        clean_data = processor.clean_data(data)
        self.assertFalse(clean_data.isnull().values.any())

    def test_model_training_process(self):
        """Testa o processo completo de treinamento do modelo"""
        with patch('apps.tenis_admin.services.ModelTrainingService.train_model') as mock_train:
            mock_train.return_value = {'status': 'success', 'model_id': 1}
            
            service = ModelTrainingService(self.dataset)
            result = service.execute()
            
            self.assertEqual(result['status'], 'success')
            self.assertIsInstance(result['model_id'], int)

    def test_metrics_calculation(self):
        """Testa o cálculo de métricas de performance"""
        test_metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85
        }
        
        with patch('apps.tenis_admin.services.MetricsService.calculate_metrics') as mock_metrics:
            mock_metrics.return_value = test_metrics
            
            metrics_service = MetricsService(self.model)
            metrics = metrics_service.get_performance_metrics()
            
            for key in test_metrics.keys():
                self.assertIn(key, metrics)
                self.assertEqual(metrics[key], test_metrics[key])

    def test_dataset_validation(self):
        """Testa a validação de datasets"""
        validation_service = DatasetService()
        
        # Teste com dataset válido
        valid_result = validation_service.validate_dataset(self.dataset)
        self.assertTrue(valid_result['is_valid'])
        
        # Teste com dataset inválido
        invalid_dataset = Dataset.objects.create(
            file="media/datasets/invalid.csv",
            description="Dataset inválido",
            is_active=True
        )
        invalid_result = validation_service.validate_dataset(invalid_dataset)
        self.assertFalse(invalid_result['is_valid'])

    def test_model_deployment(self):
        """Testa o deploy de modelos"""
        deploy_service = ModelDeploymentService()
        
        with patch('apps.tenis_admin.services.ModelDeploymentService.save_model') as mock_save:
            mock_save.return_value = True
            
            result = deploy_service.deploy_model(
                model=self.model,
                version="2.0",
                metadata={'algorithm': 'random_forest'}
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(self.model.version, "2.0")

    def test_full_analyst_workflow(self):
        """Teste completo do fluxo de trabalho do analista"""
        # 1. Processamento de dados
        processor = DataProcessor(self.dataset)
        clean_data = processor.clean_data(processor.load_data())
        
        # 2. Treinamento do modelo
        training_service = ModelTrainingService(self.dataset)
        training_result = training_service.execute()
        
        # 3. Validação do modelo
        metrics_service = MetricsService(AIModel.objects.get(pk=training_result['model_id']))
        metrics = metrics_service.get_performance_metrics()
        
        # 4. Deploy do modelo
        if metrics['accuracy'] > 0.8:
            deploy_service = ModelDeploymentService()
            deploy_result = deploy_service.deploy_model(
                model=metrics_service.model,
                version="production",
                metadata={'training_metrics': metrics}
            )
            
            self.assertTrue(deploy_result['success'])
