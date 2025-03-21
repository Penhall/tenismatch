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
            if not dataset.file:
                raise ValueError(f"Dataset {dataset_id} não possui arquivo associado")
                
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
            if not dataset.file:
                raise ValueError(f"Dataset {dataset_id} não possui arquivo associado")
                
            df = pd.read_csv(dataset.file.path, nrows=rows)
            
            # Calcular total de linhas
            with open(dataset.file.path, 'r') as f:
                total_rows = sum(1 for line in f) - 1  # -1 para o cabeçalho
            
            return {
                'columns': list(df.columns),
                'data': df.head(rows).to_dict('records'),
                'total_rows': total_rows,
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
            for target_col, original_col in mapping.items():
                if original_col not in available_columns:
                    raise ValueError(f"Coluna original '{original_col}' não existe no dataset")
                
            column_mapping.mapping = mapping
            column_mapping.is_mapped = True
            column_mapping.save()
            
            # Atualizar status do dataset
            dataset.status = 'ready'
            dataset.is_processed = True
            dataset.save()
            
            return True, "Mapeamento salvo com sucesso"
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} não encontrado")
            return False, "Dataset não encontrado"
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
            
            try:
                mapping = ColumnMapping.objects.get(dataset=dataset)
            except ColumnMapping.DoesNotExist:
                return False, {"error": "Mapeamento não encontrado"}
            
            if not mapping.is_mapped:
                return False, {"error": "Mapeamento não foi confirmado"}
            
            # Verificar se todas as colunas necessárias estão mapeadas
            required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
            missing_columns = []
            
            for col in required_columns:
                if col not in mapping.mapping:
                    missing_columns.append(col)
                    
            if missing_columns:
                return False, {
                    "error": "Mapeamento incompleto",
                    "missing_columns": missing_columns
                }
                
            return True, None
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} não encontrado")
            return False, {"error": "Dataset não encontrado"}
        except Exception as e:
            logger.error(f"Erro ao validar mapeamento do dataset {dataset_id}: {str(e)}")
            return False, {"error": str(e)}
    
    @staticmethod
    def get_mapping_suggestion(dataset_id: int) -> Dict[str, str]:
        """
        Sugere um mapeamento automático baseado em nomes de colunas similares.
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            if not dataset.file:
                raise ValueError(f"Dataset {dataset_id} não possui arquivo associado")
                
            # Obtém as colunas do dataset
            df = pd.read_csv(dataset.file.path, nrows=1)
            dataset_columns = list(df.columns)
            
            # Colunas requeridas
            required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
            
            # Dicionário para armazenar as sugestões
            suggestions = {}
            
            # Para cada coluna requerida, tenta encontrar uma correspondência
            for req_col in required_columns:
                # Primeiro tenta match exato
                if req_col in dataset_columns:
                    suggestions[req_col] = req_col
                    continue
                
                # Se não encontrar match exato, tenta similaridade
                best_match = None
                highest_similarity = 0
                
                for col in dataset_columns:
                    # Calcular similaridade simples
                    similarity = 0
                    req_words = req_col.lower().split('_')
                    col_words = col.lower().replace('_', ' ').replace('-', ' ').split()
                    
                    for word in req_words:
                        if word in col_words:
                            similarity += 1
                    
                    # Normalizar pela maior quantidade de palavras
                    similarity = similarity / max(len(req_words), len(col_words))
                    
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        best_match = col
                
                # Se encontrou uma correspondência com similaridade > 0.3
                if best_match and highest_similarity > 0.3:
                    suggestions[req_col] = best_match
            
            return suggestions
            
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} não encontrado")
            return {}
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões de mapeamento para dataset {dataset_id}: {str(e)}")
            return {}