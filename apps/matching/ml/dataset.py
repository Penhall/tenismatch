import numpy as np
import pandas as pd
from django.core.files.base import ContentFile  # Adicionado

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
                'tenis_estilo': np.random.choice(prep.styles),
                'tenis_marca': np.random.choice(prep.brands),
                'tenis_cores': np.random.choice(prep.colors),
                'tenis_preco': np.random.randint(100, 1000),
                'match_success': 1 if np.random.random() < 0.5 else 0,
            }
            
            # Calcula a probabilidade de match com base no registro
            prob = prep._calculate_match_probability(record)
            record['match_success_prob'] = prob
            
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
        prob += style_probs.get(record['tenis_estilo'], 0)
        
        # Ajusta baseado na marca
        brand_probs = {
            'Nike': 0.1,
            'Adidas': 0.1,
            'Vans': 0.05,
            'Converse': 0.05,
            'New Balance': 0.05
        }
        prob += brand_probs.get(record['tenis_marca'], 0)
        
        # Normaliza probabilidade
        return min(max(prob / 2, 0), 1)  # Garante entre 0 e 1
    
    @staticmethod
    def load_and_prepare_data(file_path):
        """Carrega e prepara dados de um arquivo CSV"""
        df = pd.read_csv(file_path)
        
        # Validações básicas
        required_columns = ['tenis_estilo', 'tenis_marca', 'tenis_cores', 'tenis_preco']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Dataset não contém todas as colunas necessárias")
            
        return df.to_dict('records')
