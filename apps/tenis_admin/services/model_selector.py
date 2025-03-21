# /tenismatch/apps/tenis_admin/services/model_selector.py
"""
Serviço para validação e seleção de modelos de ML.
"""
import pandas as pd
import numpy as np
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
            logger.info(f"Dataset carregado com sucesso: {dataset_path}")
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
            # Estatísticas básicas
            basic_stats = {
                'rows': len(self.df),
                'columns': list(self.df.columns),
                'missing_values': self.df.isnull().sum().to_dict(),
                'numeric_columns': list(self.df.select_dtypes(include=['int64', 'float64']).columns),
                'categorical_columns': list(self.df.select_dtypes(include=['object']).columns)
            }
            
            # Estatísticas numéricas
            numeric_stats = {}
            for col in basic_stats['numeric_columns']:
                numeric_stats[col] = {
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'std': float(self.df[col].std())
                }
            
            # Estatísticas categóricas
            categorical_stats = {}
            for col in basic_stats['categorical_columns']:
                # Limitar a 10 valores mais comuns para não sobrecarregar
                value_counts = self.df[col].value_counts().head(10).to_dict()
                categorical_stats[col] = {
                    'unique_values': self.df[col].nunique(),
                    'top_values': value_counts
                }
            
            return {
                'basic': basic_stats,
                'numeric': numeric_stats,
                'categorical': categorical_stats
            }
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas do dataset: {str(e)}")
            return {'error': str(e)}
    
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
                
                # Determinar tipo mais específico
                if dtype == 'object':
                    # Verificar se é categórico
                    unique_count = self.df[col].nunique()
                    total_count = len(self.df)
                    
                    if unique_count / total_count < 0.05:  # menos de 5% de valores únicos
                        dtype = 'categorical'
                    else:
                        # Tentar interpretar como data
                        try:
                            pd.to_datetime(self.df[col], errors='raise')
                            dtype = 'datetime'
                        except:
                            # Testar se é texto ou misto
                            if self.df[col].str.isnumeric().all():
                                dtype = 'string_numeric'
                            else:
                                dtype = 'text'
                
                column_types[col] = {
                    'dtype': dtype,
                    'unique_values': int(self.df[col].nunique()),
                    'missing_values': int(self.df[col].isnull().sum())
                }
                
            return column_types
        except Exception as e:
            logger.error(f"Erro ao verificar tipos das colunas: {str(e)}")
            return {}
    
    def recommend_model(self) -> str:
        """
        Recomenda o melhor modelo com base nas características do dataset.
        
        Returns:
            str: Identificador do modelo recomendado
        """
        try:
            # Informações básicas do dataset
            n_rows = len(self.df)
            n_features = len(self.df.columns) - (1 if 'label' in self.df.columns else 0)
            categorical_cols = len(self.df.select_dtypes(include=['object']).columns)
            
            # Regras de seleção (simplificadas)
            if n_rows < 100:
                # Para datasets pequenos, Regressão Logística
                return 'logistic_regression'
            elif categorical_cols / n_features > 0.5:
                # Para muitas variáveis categóricas, Random Forest
                return 'random_forest'
            else:
                # Default para datasets gerais
                return 'svm'
                
        except Exception as e:
            logger.error(f"Erro ao recomendar modelo: {str(e)}")
            return 'random_forest'  # Fallback para modelo mais robusto
    
    def get_compatible_models(self) -> list:
        """
        Retorna lista de todos os modelos compatíveis com o dataset atual.
        
        Returns:
            list: Lista de dicionários com modelos compatíveis e seus scores
        """
        compatible_models = []
        
        # Obter todos os modelos do catálogo
        all_models = ModelCatalog.get_all_models()
        
        for model in all_models:
            # Validar compatibilidade
            validation = self.validate_model_selection(model['id'])
            model['compatible'] = validation['valid']
            model['message'] = validation['message']
            
            if validation['valid']:
                # Calcular score de compatibilidade (exemplo simples)
                model['compatibility_score'] = self._calculate_compatibility_score(model['id'])
                compatible_models.append(model)
        
        # Ordenar por score de compatibilidade
        return sorted(compatible_models, key=lambda x: x['compatibility_score'], reverse=True)
    
    def _calculate_compatibility_score(self, model_type: str) -> float:
        """
        Calcula um score de compatibilidade entre o modelo e o dataset.
        
        Args:
            model_type (str): Tipo de modelo
            
        Returns:
            float: Score de compatibilidade (0-1)
        """
        try:
            # Este é um exemplo simples - em um sistema real seria mais sofisticado
            model_info = ModelCatalog.get_model_info(model_type)
            
            # Fatores para o score
            factors = {
                'sample_size': 0.0,  # Score para tamanho da amostra
                'column_match': 0.0,  # Score para correspondência de colunas
                'missing_data': 0.0,  # Score para dados faltantes
            }
            
            # Calcular score de tamanho da amostra
            min_samples = model_info['requirements']['min_samples']
            actual_samples = len(self.df)
            
            # Quanto mais amostras acima do mínimo, melhor (até 5x)
            sample_ratio = min(5, actual_samples / min_samples) / 5
            factors['sample_size'] = sample_ratio
            
            # Calcular score de correspondência de colunas
            required_cols = set(model_info['requirements']['required_columns'])
            actual_cols = set(self.df.columns)
            
            # Proporção de colunas necessárias presentes
            cols_ratio = len(required_cols.intersection(actual_cols)) / len(required_cols)
            factors['column_match'] = cols_ratio
            
            # Calcular score para dados faltantes
            missing_ratio = 1.0 - (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)))
            factors['missing_data'] = missing_ratio
            
            # Calcular score final (média ponderada)
            weights = {
                'sample_size': 0.4,
                'column_match': 0.4,
                'missing_data': 0.2
            }
            
            final_score = sum(factors[k] * weights[k] for k in factors)
            return float(final_score)
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de compatibilidade: {str(e)}")
            return 0.5  # Score neutro em caso de erro