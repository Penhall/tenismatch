import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class SneakerMatchTraining:
    def __init__(self):
        # Pesos para diferentes estilos de tênis
        self.style_weights = {
            'ESP': {'aventureiro': 0.8, 'atlético': 0.7, 'casual': 0.3},
            'CAS': {'casual': 0.9, 'social': 0.6, 'prático': 0.7},
            'VIN': {'artístico': 0.8, 'alternativo': 0.7, 'clássico': 0.6},
            'SOC': {'elegante': 0.8, 'social': 0.9, 'formal': 0.7},
            'FAS': {'moderno': 0.9, 'criativo': 0.8, 'arrojado': 0.7}
        }

        # Inicializar componentes ML
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def train_model(self, dataset_id, match_data=None):
        try:
            # Extrair features
            features = self._extract_features(dataset_id)
            
            # Dividir em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                features, 
                match_data if match_data is not None else np.zeros(len(features)),
                test_size=0.2
            )
            
            # Treinar modelo
            self.model.fit(X_train, y_train)
            
            # Avaliar modelo
            predictions = self.model.predict(X_test)
            metrics = {
                'accuracy': float(accuracy_score(y_test, predictions)),
                'precision': float(precision_score(y_test, predictions)),
                'recall': float(recall_score(y_test, predictions)),
                'f1_score': float(f1_score(y_test, predictions))
            }
            
            return True, metrics
            
        except Exception as e:
            return False, str(e)

    def _extract_features(self, dataset_id):
        """
        Extrai features do dataset para treinamento
        """
        from ..models import Dataset
        dataset = Dataset.objects.get(id=dataset_id)
        
        try:
            import pandas as pd
            df = pd.read_csv(dataset.file.path)
            
            features = []
            for _, row in df.iterrows():
                # Features do tênis
                style_features = self._get_style_features(row.get('style', 'CAS'))
                
                # Features numéricas
                numeric_features = [
                    row.get('price_range', 0) / 5.0,  # Normaliza preço
                    1 if row.get('is_premium', False) else 0,
                ]
                
                features.append(style_features + numeric_features)
            
            return np.array(features)
            
        except Exception as e:
            raise ValueError(f"Erro ao processar dataset: {str(e)}")

    def _get_style_features(self, style):
        """
        Converte estilo em vetor de features
        """
        features = []
        for trait, weight in self.style_weights.get(style, {}).items():
            features.append(weight)
        return features

    def predict_match(self, user_data, other_data):
        """
        Prediz compatibilidade entre dois usuários
        """
        # Extrai features
        user_features = self._extract_user_features(user_data)
        other_features = self._extract_user_features(other_data)
        
        # Combina features
        combined = np.concatenate([user_features, other_features])
        
        # Faz predição
        prob = self.model.predict_proba([combined])[0][1]
        
        return float(prob)

    def _extract_user_features(self, user_data):
        """
        Extrai features de um usuário
        """
        features = []
        
        # Estilo do tênis
        style_features = self._get_style_features(user_data.get('style', 'CAS'))
        features.extend(style_features)
        
        # Outras características
        features.append(user_data.get('price_range', 0) / 5.0)
        features.append(1 if user_data.get('is_premium', False) else 0)
        
        return np.array(features)