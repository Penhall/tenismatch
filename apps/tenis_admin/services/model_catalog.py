# /tenismatch/apps/tenis_admin/services/model_catalog.py
"""
Catálogo de modelos de ML disponíveis para treinamento.
Define os tipos de modelos, seus parâmetros e requisitos.
"""
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

logger = logging.getLogger(__name__)

class ModelCatalog:
    """
    Catálogo central de modelos de ML disponíveis para treinamento.
    Cada modelo inclui seus parâmetros padrão e requisitos de dados.
    """
    
    AVAILABLE_MODELS = {
        'random_forest': {
            'name': 'Random Forest Classifier',
            'class': RandomForestClassifier,
            'default_params': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42
            },
            'requirements': {
                'min_samples': 100,
                'required_columns': ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco'],
                'target_type': 'binary'
            },
            'description': 'Modelo de floresta aleatória para classificação de compatibilidade. Ideal para datasets com muitas características categóricas.'
        },
        'logistic_regression': {
            'name': 'Regressão Logística',
            'class': LogisticRegression,
            'default_params': {
                'C': 1.0,
                'random_state': 42
            },
            'requirements': {
                'min_samples': 50,
                'required_columns': ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco'],
                'target_type': 'binary'
            },
            'description': 'Regressão logística para classificação binária. Modelo simples e de fácil interpretação.'
        },
        'svm': {
            'name': 'Support Vector Machine',
            'class': SVC,
            'default_params': {
                'kernel': 'rbf',
                'C': 1.0,
                'probability': True,
                'random_state': 42
            },
            'requirements': {
                'min_samples': 50,
                'required_columns': ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco'],
                'target_type': 'binary'
            },
            'description': 'Máquina de Vetores de Suporte para classificação. Bom desempenho em espaços de alta dimensionalidade.'
        }
    }
    
    @classmethod
    def get_model_info(cls, model_type):
        """
        Retorna informações sobre um modelo específico.
        
        Args:
            model_type (str): Identificador do modelo no catálogo
            
        Returns:
            dict: Informações do modelo ou None se não encontrado
        """
        model_info = cls.AVAILABLE_MODELS.get(model_type)
        if not model_info:
            logger.warning(f"Modelo {model_type} não encontrado no catálogo")
        return model_info
    
    @classmethod
    def get_model_class(cls, model_type):
        """
        Retorna a classe do modelo para instanciação.
        
        Args:
            model_type (str): Identificador do modelo no catálogo
            
        Returns:
            class: Classe do modelo ou None se não encontrado
        """
        model_info = cls.get_model_info(model_type)
        return model_info['class'] if model_info else None
    
    @classmethod
    def get_default_params(cls, model_type):
        """
        Retorna os parâmetros padrão para um modelo.
        
        Args:
            model_type (str): Identificador do modelo no catálogo
            
        Returns:
            dict: Parâmetros padrão ou None se modelo não encontrado
        """
        model_info = cls.get_model_info(model_type)
        return model_info['default_params'] if model_info else None
    
    @classmethod
    def get_requirements(cls, model_type):
        """
        Retorna os requisitos para um modelo.
        
        Args:
            model_type (str): Identificador do modelo no catálogo
            
        Returns:
            dict: Requisitos do modelo ou None se não encontrado
        """
        model_info = cls.get_model_info(model_type)
        return model_info['requirements'] if model_info else None
    
    @classmethod
    def get_all_models(cls):
        """
        Retorna lista de todos os modelos disponíveis.
        
        Returns:
            list: Lista de dicionários com informações básicas dos modelos
        """
        models = []
        for model_id, info in cls.AVAILABLE_MODELS.items():
            models.append({
                'id': model_id,
                'name': info['name'],
                'description': info.get('description', ''),
                'min_samples': info['requirements']['min_samples']
            })
        return models
    
    @classmethod
    def create_model_instance(cls, model_type, custom_params=None):
        """
        Cria uma instância do modelo com parâmetros customizados.
        
        Args:
            model_type (str): Identificador do modelo no catálogo
            custom_params (dict, optional): Parâmetros customizados para o modelo
            
        Returns:
            object: Instância do modelo ou None se não encontrado
        """
        try:
            model_class = cls.get_model_class(model_type)
            if not model_class:
                return None
                
            # Combinar parâmetros padrão com customizados
            params = cls.get_default_params(model_type).copy()
            if custom_params:
                params.update(custom_params)
                
            return model_class(**params)
        except Exception as e:
            logger.error(f"Erro ao criar instância do modelo {model_type}: {str(e)}")
            return None