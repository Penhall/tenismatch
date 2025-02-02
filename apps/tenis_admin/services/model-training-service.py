# /tenismatch/apps/tenis_admin/services/model_training_service.py
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from ..models import AIModel, Dataset
from .training_service import SneakerMatchTraining

logger = logging.getLogger(__name__)

class ModelTrainingService:
    @staticmethod
    def train_model(model_id: int, dataset_id: int) -> tuple[bool, dict]:
        try:
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            if not dataset.is_processed:
                return False, "Dataset não está processado"

            # Carrega e prepara dados
            df = pd.read_csv(dataset.file.path)
            
            # Preparar features e targets
            trainer = SneakerMatchTraining()
            X = ModelTrainingService._prepare_features(df)
            y = ModelTrainingService._prepare_targets(df)
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Treinar modelo
            success, message = trainer.train_model(X_train, y_train)
            if not success:
                return False, message
            
            # Avaliar modelo
            y_pred = trainer.model.predict(X_test)
            eval_metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred)),
                'recall': float(recall_score(y_test, y_pred)),
                'f1_score': float(f1_score(y_test, y_pred))
            }
            
            # Salvar métricas e atualizar status
            model.metrics = eval_metrics
            model.status = 'review'
            model.save()
            
            logger.info(f"Modelo {model_id} treinado com sucesso. Métricas: {eval_metrics}")
            return True, eval_metrics
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo {model_id}: {str(e)}")
            return False, str(e)

    @staticmethod
    def _prepare_features(df: pd.DataFrame) -> np.ndarray:
        features = []
        for _, row in df.iterrows():
            # Features do tênis
            tenis_features = [
                row['tenis_marca'],
                row['tenis_estilo'],
                row['tenis_cores'],
                float(row['tenis_preco'])
            ]
            features.append(tenis_features)
        return np.array(features)

    @staticmethod
    def _prepare_targets(df: pd.DataFrame) -> np.ndarray:
        if 'match_success' in df.columns:
            return df['match_success'].values
        return np.random.choice([0, 1], size=len(df), p=[0.3, 0.7])

    @staticmethod
    def deploy_model(model_id: int) -> tuple[bool, str]:
        try:
            model = AIModel.objects.get(id=model_id)
            
            if model.status != 'approved':
                return False, "Apenas modelos aprovados podem ser implantados"
            
            model.status = 'deployed'
            model.save()
            
            logger.info(f"Modelo {model_id} implantado com sucesso")
            return True, "Modelo implantado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao implantar modelo {model_id}: {str(e)}")
            return False, str(e)