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