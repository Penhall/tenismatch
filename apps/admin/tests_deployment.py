
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import AIModel, Dataset
from .services import ModelDeploymentService
import json

class ModelDeploymentTests(TestCase):
    def setUp(self):
        self.dataset = Dataset.objects.create(
            name="Test Dataset",
            file=SimpleUploadedFile("test.csv", b"test,data\n1,2\n3,4"),
            records_count=2
        )
        
        self.model = AIModel.objects.create(
            name="Test Model",
            version="1.0",
            status="approved",
            metrics=json.dumps({
                'accuracy': 0.95,
                'precision': 0.94,
                'recall': 0.93
            })
        )

    def test_model_deployment(self):
        # Test successful deployment
        result = ModelDeploymentService.deploy_model(self.model.id)
        self.assertTrue(result)
        
        # Test deployment of non-approved model
        self.model.status = 'draft'
        self.model.save()
        
        with self.assertRaises(ValueError):
            ModelDeploymentService.deploy_model(self.model.id)

    def test_model_versioning(self):
        # Test version control during deployment
        deployed_model = ModelDeploymentService.get_deployed_model()
        self.assertEqual(deployed_model.version, "1.0")
        
        # Test deployment history
        history = ModelDeploymentService.get_deployment_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['version'], "1.0")