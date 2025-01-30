# /tenismatch/apps/tenis_admin/services/data_processor.py
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import logging
from typing import Tuple, Dict, Any, List
from ..models import Dataset, ColumnMapping

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
        dataset = Dataset.objects.get(id=dataset_id)
        
        try:
            df = cls._read_dataset_file(dataset)
            
            # Se existe mapeamento, aplicar
            if hasattr(dataset, 'column_mapping') and dataset.column_mapping.is_validated:
                df = df.rename(columns=dataset.column_mapping.mapping)
            
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
    def get_dataset_columns(cls, dataset_id: int) -> List[str]:
        """Retorna lista de colunas do dataset"""
        dataset = Dataset.objects.get(id=dataset_id)
        df = pd.read_csv(dataset.file.path, nrows=1)
        return list(df.columns)

    @classmethod
    def get_preview_data(cls, dataset_id: int, rows: int = 5) -> Dict:
        """Retorna preview dos dados para visualização"""
        dataset = Dataset.objects.get(id=dataset_id)
        df = pd.read_csv(dataset.file.path, nrows=rows)
        return {
            'columns': list(df.columns),
            'data': df.to_dict('records'),
            'total_rows': sum(1 for _ in open(dataset.file.path)) - 1
        }
        
    @classmethod
    def validate_mapping(cls, dataset_id: int, mapping: Dict[str, str]) -> Tuple[bool, str]:
        """Valida se o mapeamento proposto é válido"""
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            df = pd.read_csv(dataset.file.path, nrows=1)
            
            # Verificar se colunas existem
            for original_col in mapping.keys():
                if original_col not in df.columns:
                    return False, f"Coluna '{original_col}' não existe no dataset"
                    
            # Verificar se todos os campos necessários estão mapeados
            mapped_cols = set(mapping.values())
            for required in cls.REQUIRED_COLUMNS:
                if required not in mapped_cols:
                    return False, f"Campo obrigatório '{required}' não mapeado"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)

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