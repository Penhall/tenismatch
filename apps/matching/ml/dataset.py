# /tenismatch/apps/matching/ml/dataset.py 
import numpy as np
import pandas as pd

class DatasetPreparation:
    def __init__(self):
        self.styles = ['ESP', 'CAS', 'VIN', 'SOC', 'FAS']
        self.brands = ['Nike', 'Adidas', 'Vans', 'Converse', 'New Balance']
        self.colors = ['BLK', 'WHT', 'COL', 'NEU']
        
    @staticmethod
    def generate_training_data(n_samples=1000):
        """Gera dataset sintético para treinamento"""
        prep = DatasetPreparation()
        data = []
        
        for _ in range(n_samples):
            # Gera um registro sintético
            record = {
                'style': np.random.choice(prep.styles),
                'brand': np.random.choice(prep.brands),
                'color': np.random.choice(prep.colors),
                'price': np.random.randint(100, 1000),
                'occasion': np.random.choice(['casual', 'sport', 'formal']),
            }
            
            # Simula sucesso do match baseado em regras
            match_prob = prep._calculate_match_probability(record)
            record['match_success'] = 1 if np.random.random() < match_prob else 0
            
            data.append(record)
            
        return data
    
    def _calculate_match_probability(self, record):
        """Calcula probabilidade base de match para dados sintéticos"""
        prob = 0.5  # Probabilidade base
        
        # Ajusta baseado no estilo
        style_probs = {
            'ESP': 0.7,  # Esportivo tem alta chance
            'CAS': 0.6,  # Casual também
            'VIN': 0.5,  # Vintage médio
            'SOC': 0.4,  # Social menor
            'FAS': 0.6   # Fashion bom
        }
        prob += style_probs.get(record['style'], 0)
        
        # Ajusta baseado na marca
        brand_probs = {
            'Nike': 0.1,
            'Adidas': 0.1,
            'Vans': 0.05,
            'Converse': 0.05,
            'New Balance': 0.05
        }
        prob += brand_probs.get(record['brand'], 0)
        
        # Normaliza probabilidade
        return min(max(prob / 2, 0), 1)  # Garante entre 0 e 1
    
    @staticmethod
    def load_and_prepare_data(file_path):
        """Carrega e prepara dados de um arquivo CSV"""
        df = pd.read_csv(file_path)
        
        # Validações básicas
        required_columns = ['style', 'brand', 'color', 'price']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Dataset não contém todas as colunas necessárias")
            
        return df.to_dict('records')