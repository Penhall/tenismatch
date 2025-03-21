# /tenismatch/apps/matching/services/__init__.py
"""
Serviços para o módulo de matching do TenisMatch.
Fornece funcionalidades de recomendação e análise de compatibilidade.
"""

# Serviço principal de recomendação
from .recommender_service import RecommenderService

# Serviço de estatísticas
from .match_statistics_service import MatchStatisticsService

# Recomendadores e Factory
from .recommender_factory import RecommenderFactory
from .ml_recommender import MLRecommender
from .basic_recommender import BasicRecommender

# Adaptador para compatibilidade
from .recommender_adapter import TenisMatchRecommender