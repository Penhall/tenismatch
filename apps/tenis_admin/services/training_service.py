
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class SneakerMatchTraining:
    def __init__(self):
        self.style_weights = {
            'ESP': {'aventureiro': 0.8, 'atlético': 0.7, 'casual': 0.3},
            'CAS': {'casual': 0.9, 'social': 0.6, 'prático': 0.7},
            'VIN': {'artístico': 0.8, 'alternativo': 0.7, 'clássico': 0.6},
            'SOC': {'elegante': 0.8, 'social': 0.9, 'formal': 0.7},
            'FAS': {'moderno': 0.9, 'criativo': 0.8, 'arrojado': 0.7}
        }
        
        self.brand_weights = {
            'Nike': {'esportivo': 0.9, 'moderno': 0.8},
            'Adidas': {'esportivo': 0.8, 'casual': 0.7},
            'Vans': {'casual': 0.9, 'alternativo': 0.8},
            'Converse': {'casual': 0.8, 'artístico': 0.7},
            'New Balance': {'esportivo': 0.7, 'casual': 0.8}
        }
        
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    def preprocess_data(self, data):
        """Preprocessa os dados para treinamento"""
        X = []
        y = []
        
        for item in data:
            # Extrair features
            features = self._extract_features(item)
            X.append(features)
            # O target é o sucesso do match (0 ou 1)
            y.append(item.get('match_success', 0))
            
        return np.array(X), np.array(y)

    def _extract_features(self, item):
        """Extrai características relevantes dos dados"""
        features = []
        
        # Estilo
        style = item.get('style', 'CAS')
        style_vec = [1 if s == style else 0 for s in self.style_weights.keys()]
        features.extend(style_vec)
        
        # Marca
        brand = item.get('brand', 'Nike')
        brand_vec = [1 if b == brand else 0 for b in self.brand_weights.keys()]
        features.extend(brand_vec)
        
        # Preço normalizado
        price = item.get('price', 0)
        features.append(price / 1000.0)  # Normaliza preço
        
        return np.array(features)

    def train_model(self, training_data):
        """Treina o modelo com os dados fornecidos"""
        X, y = self.preprocess_data(training_data)
        
        # Divide em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normaliza os dados
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treina o modelo
        self.model.fit(X_train_scaled, y_train)
        
        # Faz predições
        y_pred = self.model.predict(X_test_scaled)
        
        # Calcula métricas
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred)),
            'recall': float(recall_score(y_test, y_pred)),
            'f1_score': float(f1_score(y_test, y_pred))
        }
        
        return metrics

    def predict_match(self, user1_data, user2_data):
        """Prediz a probabilidade de match entre dois usuários"""
        # Extrai features dos dois usuários
        features1 = self._extract_features(user1_data)
        features2 = self._extract_features(user2_data)
        
        # Combina as features
        combined_features = np.concatenate([features1, features2])
        
        # Normaliza
        scaled_features = self.scaler.transform([combined_features])
        
        # Prediz probabilidade
        prob = self.model.predict_proba(scaled_features)[0][1]
        
        return float(prob)