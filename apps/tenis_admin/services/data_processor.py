# /tenismatch/apps/tenis_admin/services/data_processor.py
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import logging
from typing import Tuple, Dict, Any
from ..models import Dataset

logger = logging.getLogger(__name__)

class DatasetService:
    REQUIRED_COLUMNS = [
        'tenis_marca', 
        'tenis_estilo', 
        'tenis_cores', 
        'tenis_preco'
    ]

    @classmethod
    def process_dataset(cls, dataset_id: int) -> Tuple[bool, str]:
        """
        Processa um dataset após o upload.
        
        Args:
            dataset_id: ID do dataset a ser processado
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        dataset = Dataset.objects.get(id=dataset_id)
        
        try:
            df = cls._read_dataset_file(dataset)
            cls._validate_columns(df)
            stats = cls._calculate_stats(df)
            
            dataset.records_count = len(df)
            dataset.is_processed = True
            dataset.stats = stats
            dataset.save()
            
            logger.info(f"Dataset {dataset_id} processado com sucesso")
            return True, "Dataset processado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro ao processar dataset {dataset_id}: {str(e)}")
            return False, f"Erro ao processar dataset: {str(e)}"

    @classmethod
    def get_training_data(cls, dataset_id: int) -> Dict[str, Any]:
        """
        Prepara dados do dataset para treinamento.
        
        Args:
            dataset_id: ID do dataset
            
        Returns:
            Dict contendo features e matches
        """
        dataset = Dataset.objects.get(id=dataset_id)
        df = cls._read_dataset_file(dataset)
        
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

    @staticmethod
    def _read_dataset_file(dataset: Dataset) -> pd.DataFrame:
        """Lê o arquivo do dataset baseado no tipo"""
        if dataset.file_type == 'csv':
            return pd.read_csv(dataset.file.path)
        elif dataset.file_type in ['xls', 'xlsx']:
            return pd.read_excel(dataset.file.path)
        elif dataset.file_type == 'xml':
            tree = ET.parse(dataset.file.path)
            root = tree.getroot()
            data = []
            for item in root.findall('item'):
                data.append({child.tag: child.text for child in item})
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {dataset.file_type}")

    @classmethod
    def _validate_columns(cls, df: pd.DataFrame) -> None:
        """Valida se o DataFrame tem as colunas necessárias"""
        missing = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Colunas ausentes no dataset: {', '.join(missing)}")

    @staticmethod
    def _calculate_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula estatísticas básicas do dataset"""
        return {
            'total_records': len(df),
            'brands_distribution': df['tenis_marca'].value_counts().to_dict(),
            'styles_distribution': df['tenis_estilo'].value_counts().to_dict(),
            'price_stats': {
                'mean': float(df['tenis_preco'].mean()),
                'median': float(df['tenis_preco'].median()),
                'min': float(df['tenis_preco'].min()),
                'max': float(df['tenis_preco'].max())
            }
        }