"""
Serviço para validação e seleção de modelos de ML.
"""
import pandas as pd
import logging
from .model_catalog import ModelCatalog

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    Classe responsável por validar a seleção de modelos e verificar
    compatibilidade com os dados.
    """
    
    def __init__(self, dataset_path):
        """
        Inicializa o seletor de modelos.
        
        Args:
            dataset_path (str): Caminho para o arquivo do dataset
        """
        self.dataset_path = dataset_path
        self.df = None
        try:
            self.df = pd.read_csv(dataset_path)
        except Exception as e:
            logger.error(f"Erro ao ler dataset {dataset_path}: {str(e)}")
            raise ValueError(f"Não foi possível ler o dataset: {str(e)}")
    
    def validate_model_selection(self, model_type: str) -> dict:
        """
        Valida se um modelo pode ser usado com o dataset atual.
        
        Args:
            model_type (str): Tipo do modelo a ser validado
            
        Returns:
            dict: Resultado da validação com status e mensagem
        """
        try:
            # Obtém requisitos do modelo
            requirements = ModelCatalog.get_requirements(model_type)
            if not requirements:
                return {
                    'valid': False,
                    'message': f'Modelo {model_type} não encontrado no catálogo'
                }
            
            # Valida número mínimo de amostras
            if len(self.df) < requirements['min_samples']:
                return {
                    'valid': False,
                    'message': f'Dataset precisa ter pelo menos {requirements["min_samples"]} amostras'
                }
            
            # Valida colunas requeridas
            missing_columns = []
            for col in requirements['required_columns']:
                if col not in self.df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return {
                    'valid': False,
                    'message': f'Colunas ausentes no dataset: {", ".join(missing_columns)}'
                }
            
            # Valida tipo do target (se existir coluna 'label')
            if 'label' in self.df.columns and requirements['target_type'] == 'binary':
                unique_values = self.df['label'].nunique()
                if unique_values != 2:
                    return {
                        'valid': False,
                        'message': f'Para classificação binária, a coluna label deve ter exatamente 2 valores únicos'
                    }
            
            return {
                'valid': True,
                'message': 'Dataset é compatível com o modelo selecionado'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar seleção do modelo: {str(e)}")
            return {
                'valid': False,
                'message': f'Erro ao validar modelo: {str(e)}'
            }
    
    def get_dataset_stats(self) -> dict:
        """
        Retorna estatísticas básicas do dataset.
        
        Returns:
            dict: Estatísticas do dataset
        """
        try:
            return {
                'rows': len(self.df),
                'columns': list(self.df.columns),
                'missing_values': self.df.isnull().sum().to_dict(),
                'numeric_columns': list(self.df.select_dtypes(include=['int64', 'float64']).columns),
                'categorical_columns': list(self.df.select_dtypes(include=['object']).columns)
            }
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas do dataset: {str(e)}")
            return {}
    
    def check_column_types(self) -> dict:
        """
        Verifica os tipos de dados das colunas requeridas.
        
        Returns:
            dict: Mapeamento de colunas e seus tipos
        """
        try:
            column_types = {}
            for col in self.df.columns:
                dtype = str(self.df[col].dtype)
                if dtype == 'object':
                    # Tenta identificar se é categórico
                    unique_count = self.df[col].nunique()
                    total_count = len(self.df)
                    if unique_count / total_count < 0.05:  # menos de 5% de valores únicos
                        dtype = 'categorical'
                column_types[col] = dtype
            return column_types
        except Exception as e:
            logger.error(f"Erro ao verificar tipos das colunas: {str(e)}")
            return {}
