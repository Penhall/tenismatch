# /tenismatch/apps/tenis_admin/services/__init__.py
"""
Serviços do módulo de administração do TenisMatch.
Este arquivo exporta todos os serviços disponíveis para uso nas views e outros módulos.
"""

# Serviços de Dataset e Mapeamento
from .dataset_service import DatasetService
from .mapping_service import DatasetMappingService

# Serviços de Treinamento e Modelo
from .training_service import SneakerMatchTraining
from .model_training_service import ModelTrainingService
from .auto_training_service import AutoTrainingService

# Serviços de Catálogo e Seleção de Modelos
from .model_catalog import ModelCatalog
from .model_selector import ModelSelector

# Serviços de Métricas
from .metrics_service import MetricsService

# Alias para compatibilidade com código existente
# A funcionalidade de deploy foi incorporada no ModelTrainingService
ModelDeploymentService = ModelTrainingService

# Serviços de Processamento de datasets
from .data_processor import DataProcessorService
from .data_generation_service import DataGenerationService

__all__ = [
    'SneakerMatchTraining',
    'ModelTrainingService',
    'ModelDeploymentService',
    'AutoTrainingService',
    'MetricsService',
    'DatasetService',
    'DataGenerationService',
    'DatasetMappingService',
    'ModelCatalog',
    'ModelSelector',
]