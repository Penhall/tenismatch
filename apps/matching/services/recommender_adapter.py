# /tenismatch/apps/matching/services/recommender_adapter.py
"""
Adaptador para manter compatibilidade com o código legado que usa TenisMatchRecommender.
Este módulo fornece uma classe com a mesma interface que a antiga classe de recomendação,
mas internamente usa o novo RecommenderService.
"""
import logging
from .recommender_service import RecommenderService

logger = logging.getLogger(__name__)

class TenisMatchRecommender:
    """
    Classe compatível com o código legado.
    Implementa a mesma interface que a classe original,
    mas usa o novo RecommenderService internamente.
    """
    def __init__(self):
        self.recommender = RecommenderService()
    
    def get_recommendations(self, user_profile, limit=5):
        """
        Mantém a assinatura original para compatibilidade.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            
        Returns:
            list: Lista de tuplas (profile, score) para compatibilidade com código legado
        """
        try:
            # Obter recomendações do novo serviço
            recommendations = self.recommender.get_matches(user_profile, limit)
            
            # Converter para o formato esperado pelo código legado
            legacy_format = []
            for rec in recommendations:
                profile = rec['profile']
                score = rec.get('adjusted_score', rec.get('compatibility', 0))
                legacy_format.append((profile, score))
            
            return legacy_format
        except Exception as e:
            logger.error(f"Erro no adaptador de recomendação: {str(e)}")
            return []
    
    def calculate_compatibility(self, user_profile, other_profile):
        """
        Calcula compatibilidade entre dois perfis.
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            float: Score de compatibilidade
        """
        try:
            # Usar o novo serviço
            match_info = self.recommender.get_single_match(user_profile, other_profile)
            return match_info.get('compatibility', 0.5)
        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade: {str(e)}")
            return 0.5  # Score neutro em caso de erro
    
    def get_common_interests(self, user_a_profile, user_b_profile):
        """
        Implementa a funcionalidade do método original.
        
        Args:
            user_a_profile: Perfil do usuário A
            user_b_profile: Perfil do usuário B
            
        Returns:
            list: Lista de interesses comuns
        """
        try:
            interests = set()
            
            # Adiciona interesses baseados no estilo do tênis
            if user_a_profile.style == user_b_profile.style:
                interests.add('Estilo de Tênis')
                
            # Adiciona interesses baseados na marca
            if user_a_profile.brand == user_b_profile.brand:
                interests.add('Marca Favorita')
                
            # Adiciona interesses baseados na ocasião, se disponível
            if hasattr(user_a_profile, 'occasion') and hasattr(user_b_profile, 'occasion'):
                if user_a_profile.occasion == user_b_profile.occasion:
                    interests.add('Ocasião de Uso')
                    
            # Obter razões de compatibilidade do novo sistema
            match_info = self.recommender.get_single_match(user_a_profile, user_b_profile)
            if 'reasons' in match_info:
                for reason in match_info['reasons']:
                    # Converter razões em interesses
                    if "mesma marca" in reason.lower():
                        interests.add('Marca Favorita')
                    elif "mesmo estilo" in reason.lower():
                        interests.add('Estilo de Tênis')
                    elif "cores" in reason.lower():
                        interests.add('Preferências de Cores')
                    elif "preço" in reason.lower():
                        interests.add('Faixa de Preço')
            
            return list(interests)
        except Exception as e:
            logger.error(f"Erro ao obter interesses comuns: {str(e)}")
            return []