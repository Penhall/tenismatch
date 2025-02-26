import numpy as np
import pandas as pd  # Adicionando importação de pandas
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from django.db import transaction
from apps.tenis_admin.models import AIModel, Dataset
from django.contrib.auth import get_user_model
from django.conf import settings
import logging  # Adicionando importação de logging

logger = logging.getLogger(__name__)

User = get_user_model()

class SneakerMatchTraining:
    def __init__(self):
        self.style_weights = {
            'ESP': {'aventureiro': 0.8, 'atlético': 0.7, 'casual': 0.3},
            'CAS': {'casual': 0.9, 'social': 0.6, 'prático': 0.7},
            'VIN': {'artístico': 0.8, 'alternativo': 0.7, 'clássico': 0.6},
            'SOC': {'elegante': 0.8, 'social': 0.9, 'formal': 0.7},
            'FAS': {'moderno': 0.9, 'criativo': 0.8, 'arrojado': 0.7}
        }

        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def train_model(self, X_train, y_train):
        try:
            # Treinar modelo
            self.model.fit(X_train, y_train)
            return True, "Modelo treinado com sucesso"
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return False, str(e)

    def predict_match(self, features):
        try:
            return self.model.predict_proba([features])[0][1]
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise ValueError(f"Erro na predição: {str(e)}")

    def train(self, dataset_path):
        """
        Método para treinar o modelo com um dataset
        """
        try:
            # Carregar o dataset
            df = pd.read_csv(dataset_path)
            logger.info(f"Dataset carregado com sucesso: {dataset_path}")
            
            # Verificar se o dataset tem as colunas necessárias
            required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Coluna {col} não encontrada no dataset")
                    return False, f"Coluna {col} não encontrada no dataset"
            
            # Verificar se tem a coluna de label
            if 'label' not in df.columns:
                logger.warning("Coluna 'label' não encontrada no dataset. Usando valores aleatórios.")
                # Criar labels aleatórios para teste
                import numpy as np
                df['label'] = np.random.randint(0, 2, size=len(df))
            
            # Preparar features e target
            features = df[required_columns]
            target = df['label']
            
            # Codificação categórica
            features_encoded = pd.get_dummies(features, columns=['tenis_marca', 'tenis_estilo', 'tenis_cores'])
            
            # Escalonamento
            X = self.scaler.fit_transform(features_encoded)
            y = target.values
            
            # Divisão dos dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Treinamento
            success, message = self.train_model(X_train, y_train)
            if not success:
                return False, message
            
            # Avaliação
            y_pred = self.model.predict(X_test)
            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, zero_division=0)),
                'recall': float(recall_score(y_test, y_pred, zero_division=0)),
                'f1_score': float(f1_score(y_test, y_pred, zero_division=0))
            }
            
            logger.info(f"Modelo treinado com sucesso. Métricas: {metrics}")
            return True, metrics
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return False, str(e)

class ModelTrainingService:
    def __init__(self):
        self.training = SneakerMatchTraining()

    @staticmethod
    def train_model(model_id, dataset_id):
        """
        Treina um modelo de IA usando o dataset especificado
        """
        try:
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            if dataset.status != 'ready':
                logger.error(f"Dataset {dataset_id} não está pronto para treinamento. Status: {dataset.status}")
                return False, f"Dataset não está pronto para treinamento. Status: {dataset.status}"
            
            # Verificar se o arquivo do dataset existe
            if not dataset.file or not dataset.file.path:
                logger.error(f"Arquivo do dataset {dataset_id} não encontrado")
                return False, "Arquivo do dataset não encontrado"
            
            # Verificar se o modelo está em estado válido
            if model.status not in ['draft']:
                logger.error(f"Modelo {model_id} não está em estado válido para treinamento. Status: {model.status}")
                return False, f"Modelo não está em estado válido para treinamento. Status: {model.status}"
            
            # Treinar o modelo
            trainer = SneakerMatchTraining()
            success, result = trainer.train(dataset.file.path)
            
            if success:
                # Se o resultado for um dicionário de métricas, salvar no modelo
                if isinstance(result, dict):
                    model.metrics = result
                
                model.status = 'review'
                model.save()
                logger.info(f"Modelo {model_id} treinado com sucesso e enviado para revisão")
                return True, "Modelo treinado com sucesso e enviado para revisão"
            else:
                logger.error(f"Falha ao treinar modelo {model_id}: {result}")
                return False, result
            
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} não encontrado")
            return False, "Dataset não encontrado"
            
        except AIModel.DoesNotExist:
            logger.error(f"Modelo {model_id} não encontrado")
            return False, "Modelo não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo {model_id}: {str(e)}")
            return False, str(e)

    @staticmethod
    def review_model(model_id, approved, review_notes=None):
        """
        Processa a revisão de um modelo, aprovando ou rejeitando
        """
        try:
            model = AIModel.objects.get(id=model_id)
            
            if model.status != 'review':
                logger.error(f"Modelo {model_id} não está em estado de revisão. Status: {model.status}")
                return False, f"Modelo não está em estado de revisão. Status: {model.status}"
            
            model.status = 'approved' if approved else 'rejected'
            model.save()
            
            logger.info(f"Modelo {model_id} {'aprovado' if approved else 'rejeitado'}")
            return True, "Revisão processada com sucesso"
            
        except AIModel.DoesNotExist:
            logger.error(f"Modelo {model_id} não encontrado")
            return False, "Modelo não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao processar revisão do modelo {model_id}: {str(e)}")
            return False, str(e)
