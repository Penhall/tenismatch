import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from django.db import transaction
from apps.tenis_admin.models import AIModel, Dataset
from django.contrib.auth import get_user_model
from django.conf import settings

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
            return False, str(e)

    def predict_match(self, features):
        try:
            return self.model.predict_proba([features])[0][1]
        except Exception as e:
            raise ValueError(f"Erro na predição: {str(e)}")

class ModelTrainingService:
    def __init__(self):
        self.training = SneakerMatchTraining()

    @transaction.atomic
    def train_model(self, ai_model_id, dataset_id):
        """
        Treina o modelo AIModel com base no Dataset fornecido.
        """
        try:
            ai_model = AIModel.objects.select_for_update().get(id=ai_model_id)
            dataset = Dataset.objects.select_for_update().get(id=dataset_id)

            if not dataset.is_processed:
                return False, "Dataset não está processado."

            # Carregar os dados
            data_path = dataset.file.path
            df = pd.read_csv(data_path)
            
            # Pré-processamento
            features = df[['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']]
            labels = df.get('label')  # Certifique-se de que a coluna 'label' existe

            # Codificação categórica
            features_encoded = pd.get_dummies(features, columns=['tenis_marca', 'tenis_estilo', 'tenis_cores'])

            # Escalonamento
            X = self.training.scaler.fit_transform(features_encoded)
            y = labels.values

            # Divisão dos dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Treinamento
            success, message = self.training.train_model(X_train, y_train)
            if not success:
                return False, message

            # Avaliação
            y_pred = self.training.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }

            # Atualizar AIModel com métricas
            ai_model.metrics = metrics
            ai_model.status = 'approved' if accuracy > 0.8 else 'review'
            ai_model.save()

            return True, "Modelo treinado e avaliado com sucesso."

        except AIModel.DoesNotExist:
            return False, "AIModel não encontrado."
        except Dataset.DoesNotExist:
            return False, "Dataset não encontrado."
        except Exception as e:
            # Rolar transação em caso de erro
            transaction.set_rollback(True)
            return False, str(e)
