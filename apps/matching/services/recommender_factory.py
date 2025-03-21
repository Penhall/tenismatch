# /tenismatch/apps/matching/services/recommender_factory.py
import logging
from django.conf import settings
from .ml_recommender import MLRecommender
from .basic_recommender import BasicRecommender

logger = logging.getLogger(__name__)

class RecommenderFactory:
    """
    Factory para criação de instâncias de recomendadores.
    Decide qual implementação usar com base em configurações e disponibilidade.
    """
    
    @staticmethod
    def get_recommender(recommender_type=None):
        """
        Retorna uma instância do recomendador especificado.
        
        Args:
            recommender_type (str, optional): Tipo de recomendador ('ml', 'basic' ou None para automático)
            
        Returns:
            BaseRecommender: Instância do recomendador
        """
        try:
            # Se o tipo for explicitamente especificado
            if recommender_type == 'basic':
                logger.info("Usando recomendador básico por solicitação explícita")
                return BasicRecommender()
                
            if recommender_type == 'ml':
                logger.info("Usando recomendador ML por solicitação explícita")
                return MLRecommender()
            
            # Decisão automática baseada em configuração
            use_ml = getattr(settings, 'USE_ML_RECOMMENDER', True)
            
            if use_ml:
                logger.info("Usando recomendador ML (automático)")
                return MLRecommender()
            else:
                logger.info("Usando recomendador básico (automático)")
                return BasicRecommender()
                
        except Exception as e:
            logger.error(f"Erro ao criar recomendador: {str(e)}")
            # Fallback para recomendador básico em caso de erro
            logger.info("Usando recomendador básico como fallback devido a erro")
            return BasicRecommender()
    
    @staticmethod
    def test_recommenders(user_profile, limit=5):
        """
        Testa diferentes recomendadores e compara os resultados.
        Útil para debug e avaliação.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            
        Returns:
            dict: Dicionário com resultados de cada recomendador
        """
        try:
            results = {}
            
            # Testar recomendador básico
            basic = BasicRecommender()
            basic_recommendations = basic.get_recommendations(user_profile, limit)
            results['basic'] = {
                'recommendations': basic_recommendations,
                'time_taken': 0  # Implementar timing se necessário
            }
            
            # Testar recomendador ML
            ml = MLRecommender()
            ml_recommendations = ml.get_recommendations(user_profile, limit)
            results['ml'] = {
                'recommendations': ml_recommendations,
                'time_taken': 0  # Implementar timing se necessário
            }
            
            # Calcular diferenças
            basic_profiles = {r['profile'].id for r in basic_recommendations}
            ml_profiles = {r['profile'].id for r in ml_recommendations}
            
            results['summary'] = {
                'overlap': len(basic_profiles.intersection(ml_profiles)),
                'basic_unique': len(basic_profiles - ml_profiles),
                'ml_unique': len(ml_profiles - basic_profiles)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao testar recomendadores: {str(e)}")
            return {'error': str(e)}