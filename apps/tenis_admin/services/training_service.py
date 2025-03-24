# /tenismatch/apps/tenis_admin/services/training_service.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
import os
import joblib
import re

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
                'accuracy': float(accuracy_score(y_test, y_pred) * 100),
                'precision': float(precision_score(y_test, y_pred, zero_division=0) * 100),
                'recall': float(recall_score(y_test, y_pred, zero_division=0) * 100),
                'f1_score': float(f1_score(y_test, y_pred, zero_division=0) * 100)
            }
            
            # Criar nome de arquivo seguro para Windows
            # Extrair apenas o nome do arquivo do caminho completo
            base_filename = os.path.basename(dataset_path)
            
            # Limpar o nome do arquivo para garantir compatibilidade com sistemas de arquivos
            safe_filename = re.sub(r'[\\/*?:"<>|]', "_", base_filename)
            model_filename = f'model_{safe_filename}.joblib'
            
            # Salvar o modelo treinado
            model_dir = os.path.join(settings.MEDIA_ROOT, 'models')
            os.makedirs(model_dir, exist_ok=True)
            model_file = os.path.join(model_dir, model_filename)
            
            # Salvar o modelo
            joblib.dump(self.model, model_file)
            
            logger.info(f"Modelo salvo em: {model_file}")
            logger.info(f"Modelo treinado com sucesso. Métricas: {metrics}")
            return True, metrics
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo: {str(e)}")
            return False, str(e)
    
    def extract_features(self, sneaker_data):
        """
        Extrai características relevantes de um tênis
        """
        features = {
            'marca_score': self._get_brand_score(sneaker_data.get('tenis_marca')),
            'estilo_score': self._get_style_score(sneaker_data.get('tenis_estilo')),
            'cores_score': self._get_color_score(sneaker_data.get('tenis_cores')),
            'preco_score': self._get_price_score(sneaker_data.get('tenis_preco'))
        }
        return features
    
    def _get_style_score(self, style):
        """
        Calcula pontuação baseada no estilo do tênis
        """
        if not style:
            return 0.5
        
        # Mapeamento de estilo para pontuação de 0 a 1
        style_mapping = {
            'ESP': 0.8,  # Esportivo
            'CAS': 0.6,  # Casual
            'VIN': 0.4,  # Vintage
            'SOC': 0.3,  # Social
            'FAS': 0.7,  # Fashion
        }
        
        return style_mapping.get(style[:3].upper(), 0.5)
    
    def _get_brand_score(self, brand):
        """
        Calcula pontuação baseada na marca do tênis
        """
        if not brand:
            return 0.5
        
        # Pontuação de popularidade das marcas
        brand_mapping = {
            'Nike': 0.9,
            'Adidas': 0.85,
            'Puma': 0.7,
            'Reebok': 0.65,
            'New Balance': 0.6,
            'Converse': 0.55,
            'Vans': 0.5,
            'Asics': 0.45
        }
        
        return brand_mapping.get(brand, 0.4)
    
    def _get_color_score(self, color):
        """
        Calcula pontuação baseada na cor do tênis
        """
        if not color:
            return 0.5
        
        # Pontuação de versatilidade das cores
        color_mapping = {
            'Preto': 0.9,
            'Branco': 0.85,
            'Cinza': 0.8,
            'Azul': 0.7,
            'Vermelho': 0.6,
            'Verde': 0.5,
            'Amarelo': 0.4,
            'Rosa': 0.3
        }
        
        return color_mapping.get(color, 0.5)
    
    def _get_price_score(self, price):
        """
        Calcula pontuação baseada no preço do tênis
        """
        if not price or not isinstance(price, (int, float)):
            return 0.5
        
        # Normalizar preço entre 0 e 1 (assumindo range de 0 a 2000)
        normalized = min(1.0, max(0.0, price / 2000))
        return normalized