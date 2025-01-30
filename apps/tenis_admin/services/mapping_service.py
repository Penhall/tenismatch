# /tenismatch/apps/tenis_admin/services/mapping_service.py
import pandas as pd
import logging
from ..models import Dataset, ColumnMapping
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class DatasetMappingService:
    @staticmethod
    def get_dataset_columns(dataset_id: int) -> List[str]:
        """
        Retorna lista de colunas do dataset.
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            df = pd.read_csv(dataset.file.path, nrows=1)
            return list(df.columns)
        except Exception as e:
            logger.error(f"Erro ao ler colunas do dataset {dataset_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_dataset_preview(dataset_id: int, rows: int = 5) -> Dict:
        """
        Retorna preview dos dados do dataset.
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            df = pd.read_csv(dataset.file.path, nrows=rows)
            return {
                'columns': list(df.columns),
                'data': df.to_dict('records'),
                'total_rows': len(pd.read_csv(dataset.file.path)),
            }
        except Exception as e:
            logger.error(f"Erro ao gerar preview do dataset {dataset_id}: {str(e)}")
            raise
    
    @staticmethod
    def create_or_update_mapping(dataset_id: int, mapping: Dict[str, str]) -> Tuple[bool, str]:
        """
        Cria ou atualiza o mapeamento de colunas.
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            column_mapping, created = ColumnMapping.objects.get_or_create(dataset=dataset)
            
            # Validar mapeamento
            available_columns = DatasetMappingService.get_dataset_columns(dataset_id)
            for original_col, mapped_col in mapping.items():
                if original_col not in available_columns:
                    raise ValueError(f"Coluna original '{original_col}' não existe no dataset")
                
            column_mapping.mapping = mapping
            column_mapping.is_validated = True
            column_mapping.save()
            
            return True, "Mapeamento salvo com sucesso"
        except Exception as e:
            logger.error(f"Erro ao criar mapeamento para dataset {dataset_id}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def validate_mapping(dataset_id: int) -> Tuple[bool, Optional[Dict]]:
        """
        Valida o mapeamento existente.
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            mapping = dataset.column_mapping
            
            if not mapping:
                return False, {"error": "Mapeamento não encontrado"}
            
            missing = mapping.get_missing_mappings()
            if missing:
                return False, {
                    "error": "Mapeamento incompleto",
                    "missing_columns": missing
                }
                
            return True, None
        except Exception as e:
            logger.error(f"Erro ao validar mapeamento do dataset {dataset_id}: {str(e)}")
            return False, {"error": str(e)}