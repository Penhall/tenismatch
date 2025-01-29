import pandas as pd
import numpy as np
from ..models import Dataset
import xml.etree.ElementTree as ET

class DatasetService:
    @staticmethod
    def process_dataset(dataset_id):
        dataset = Dataset.objects.get(id=dataset_id)
        try:
            if dataset.file_type == 'csv':
                df = pd.read_csv(dataset.file.path)
            elif dataset.file_type in ['xls', 'xlsx']:
                df = pd.read_excel(dataset.file.path)
            elif dataset.file_type == 'xml':
                tree = ET.parse(dataset.file.path)
                root = tree.getroot()
                data = []
                for item in root.findall('item'):
                    data.append({child.tag: child.text for child in item})
                df = pd.DataFrame(data)
            else:
                raise ValueError(f"Tipo de arquivo não suportado: {dataset.file_type}")
            
            # Valida colunas necessárias
            required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Dataset não contém todas as colunas necessárias")
            
            # Processa dados
            dataset.records_count = len(df)
            dataset.is_processed = True
            
            # Salva estatísticas básicas
            stats = {
                'total_records': len(df),
                'brands_distribution': df['tenis_marca'].value_counts().to_dict(),
                'styles_distribution': df['tenis_estilo'].value_counts().to_dict(),
                'price_stats': {
                    'mean': df['tenis_preco'].mean(),
                    'median': df['tenis_preco'].median(),
                    'min': df['tenis_preco'].min(),
                    'max': df['tenis_preco'].max()
                }
            }
            dataset.stats = stats
            dataset.save()
            
            return True, "Dataset processado com sucesso"
        except Exception as e:
            return False, f"Erro ao processar dataset: {str(e)}"

    @staticmethod
    def get_training_data(dataset_id):
        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file.path)
        elif dataset.file_type in ['xls', 'xlsx']:
            df = pd.read_excel(dataset.file.path)
        elif dataset.file_type == 'xml':
            tree = ET.parse(dataset.file.path)
            root = tree.getroot()
            data = []
            for item in root.findall('item'):
                data.append({child.tag: child.text for child in item})
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {dataset.file_type}")
        
        # Prepara dados para treinamento
        training_data = {
            'features': [],
            'matches': []
        }
        
        for _, row in df.iterrows():
            features = {
                'brand': row['tenis_marca'],
                'style': row['tenis_estilo'],
                'color': row['tenis_cores'],
                'price_range': float(row['tenis_preco'])
            }
            training_data['features'].append(features)
            training_data['matches'].append(row.get('match_success', 0))
            
        return training_data
