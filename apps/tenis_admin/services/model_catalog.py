"""
Catálogo de modelos de ML disponíveis para treinamento.
Define os tipos de modelos, seus parâmetros e requisitos.
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

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
            }
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
            }
        },
        'svm': {
            'name': 'Support Vector Machine',
            'class': SVC,
            'default_params': {
                'kernel': 'rbf',
                'C': 1.0,
                'random_state': 42
            },
            'requirements': {
                'min_samples': 50,
                'required_columns': ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco'],
                'target_type': 'binary'
            }
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
        return cls.AVAILABLE_MODELS.get(model_type)
    
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
