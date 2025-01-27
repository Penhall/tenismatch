# /tenismatch/apps/matching/ml/dataset.py 
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DatasetPreparation:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def load_data(self, filename='tenis_match_dataset.csv'):
        self.df = pd.read_csv(filename)
        return self.df
        
    def preprocess_data(self):
        # Codificação one-hot para variáveis categóricas
        categorical_features = ['tenis_marca', 'tenis_estilo', 'tenis_cores']
        self.df_encoded = pd.get_dummies(self.df, columns=categorical_features)
        
        # Normalização de features numéricas
        numeric_features = ['idade', 'matches_realizados', 'taxa_resposta']
        self.df_encoded[numeric_features] = self.scaler.fit_transform(self.df_encoded[numeric_features])
        
        return self.df_encoded
        
    def create_feature_matrix(self):
        features = self.df_encoded.drop(['user_id', 'relacionamentos_formados'], axis=1)
        target = self.df_encoded['relacionamentos_formados']
        
        return features, target
        
    @staticmethod
    def generate_training_data(num_samples=1000):
        """Gera dados sintéticos para treinamento do modelo de matching de tênis"""
        np.random.seed(42)
        
        # Gera dados básicos
        user_ids = np.arange(1, num_samples + 1)
        idades = np.random.normal(25, 5, num_samples).astype(int)
        matches_realizados = np.random.poisson(15, num_samples)
        taxa_resposta = np.random.uniform(0.1, 0.9, num_samples)
        
        # Gera dados categóricos
        marcas = np.random.choice(['Nike', 'Adidas', 'Puma', 'Asics'], num_samples)
        estilos = np.random.choice(['Corrida', 'Casual', 'Tênis', 'Basquete'], num_samples)
        cores = np.random.choice(['Preto', 'Branco', 'Azul', 'Vermelho'], num_samples)
        
        # Gera target (relacionamentos formados)
        relacionamentos = np.random.binomial(1, 0.3, num_samples)
        
        # Cria DataFrame
        df = pd.DataFrame({
            'user_id': user_ids,
            'idade': idades,
            'matches_realizados': matches_realizados,
            'taxa_resposta': taxa_resposta,
            'tenis_marca': marcas,
            'tenis_estilo': estilos,
            'tenis_cores': cores,
            'relacionamentos_formados': relacionamentos
        })
        
        return df
