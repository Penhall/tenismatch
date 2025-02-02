import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from .models import Dataset, AIModel

class DatasetService:
    @staticmethod
    def process_dataset(dataset_id):
        """Processa o dataset validando antes de marcar como processado"""
        is_valid, error = DatasetService.validate_dataset(dataset_id)
        if is_valid:
            dataset = Dataset.objects.get(id=dataset_id)
            dataset.is_processed = True
            dataset.save()
            return True, None
        else:
            return False, error

    @staticmethod
    def validate_dataset(dataset_id):
        """Valida o dataset e marca como processado se válido"""
        dataset = Dataset.objects.get(id=dataset_id)
        required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
        
        try:
            df = pd.read_csv(dataset.file.path)
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Colunas ausentes no dataset: {', '.join(missing_columns)}"
            
            # Implementar lógica adicional de processamento, se necessário
            
            dataset.is_processed = True
            dataset.save()
            return True, None
        except Exception as e:
            return False, f"Erro ao validar dataset: {str(e)}"

class ModelTrainingService:
    @staticmethod
    def train_model(model_id, dataset_id):
        model = AIModel.objects.get(id=model_id)
        dataset = Dataset.objects.get(id=dataset_id)
        
        try:
            df = pd.read_csv(dataset.file.path)
            # Implementar lógica de treinamento real aqui
            
            # Simulação de métricas para demonstração
            metrics = {
                'accuracy': np.random.uniform(0.8, 0.95),
                'precision': np.random.uniform(0.8, 0.95),
                'recall': np.random.uniform(0.8, 0.95),
                'f1_score': np.random.uniform(0.8, 0.95)
            }
            
            model.metrics = metrics
            model.status = 'review'
            model.save()
            return True
        except Exception as e:
            print(f"Erro no treinamento: {str(e)}")
            return False

class ModelDeploymentService:
    @staticmethod
    def deploy_model(model_id):
        model = AIModel.objects.get(id=model_id)
        if model.status != 'approved':
            raise ValueError("Apenas modelos aprovados podem ser implantados")
        
        try:
            # Implementar lógica de deploy real aqui
            return True
        except Exception as e:
            print(f"Erro no deploy: {str(e)}")
            return False

    @staticmethod
    def get_predictions(model_id, data):
        model = AIModel.objects.get(id=model_id)
        if model.status != 'approved':
            raise ValueError("Apenas modelos aprovados podem ser usados")
        
        try:
            # Implementar lógica de predição real aqui
            return np.random.uniform(0, 1, size=len(data))
        except Exception as e:
            print(f"Erro na predição: {str(e)}")
            return None
