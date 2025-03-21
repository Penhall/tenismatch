# /tenismatch/apps/matching/services/recommender_service.py
import logging
from .recommender_factory import RecommenderFactory
from ..models import Match

logger = logging.getLogger(__name__)

class RecommenderService:
    """
    Serviço principal para recomendações, encapsulando a lógica de
    recomendação e servindo como ponto de entrada para as views.
    """
    
    def __init__(self, recommender_type=None):
        """
        Inicializa o serviço de recomendação.
        
        Args:
            recommender_type (str, optional): Tipo de recomendador a ser usado
        """
        self.recommender = RecommenderFactory.get_recommender(recommender_type)
    
    def get_matches(self, user_profile, limit=5, save_to_db=True):
        """
        Obtém recomendações de perfis compatíveis e opcionalmente salva no banco.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            save_to_db: Se deve salvar os matches no banco
            
        Returns:
            list: Lista de dicionários com perfis recomendados e scores
        """
        try:
            # Obter recomendações do recomendador
            recommendations = self.recommender.get_recommendations(user_profile, limit)
            
            # Se solicitado, salvar matches no banco
            if save_to_db:
                self._save_matches_to_db(user_profile, recommendations)
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao obter matches: {str(e)}")
            return []
    
    def get_single_match(self, user_profile, other_profile):
        """
        Calcula a compatibilidade entre dois perfis específicos.
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            dict: Dicionário com informações de compatibilidade
        """
        try:
            # Calcular compatibilidade
            compatibility = self.recommender.calculate_compatibility(
                user_profile, 
                other_profile
            )
            
            # Obter razões para a compatibilidade
            reasons = self.recommender.get_compatibility_reasons(
                user_profile,
                other_profile
            )
            
            # Criar objeto de match
            match_info = {
                'profile': other_profile,
                'compatibility': compatibility,
                'reasons': reasons
            }
            
            return match_info
            
        except Exception as e:
            logger.error(f"Erro ao calcular match individual: {str(e)}")
            return {
                'profile': other_profile,
                'compatibility': 0.5,  # Valor neutro
                'reasons': ["Erro ao calcular compatibilidade"]
            }
    
    def get_match_suggestions(self, user_profile, limit=3):
        """
        Retorna sugestões de match diárias para o usuário.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de sugestões
            
        Returns:
            list: Lista de perfis sugeridos
        """
        try:
            # Verificar se já existem sugestões recentes
            from ..models import DailyRecommendation
            import datetime
            
            # Obter recomendações salvas hoje
            today = datetime.date.today()
            recent_recommendations = DailyRecommendation.objects.filter(
                user=user_profile.user,
                created_at__date=today
            )
            
            if recent_recommendations.count() >= limit:
                # Retornar recomendações já existentes
                return [{
                    'profile': rec.recommended_profile,
                    'compatibility': rec.compatibility_score,
                    'reasons': rec.get_reasons()
                } for rec in recent_recommendations[:limit]]
            
            # Caso contrário, gerar novas recomendações
            recommendations = self.recommender.get_recommendations(user_profile, limit)
            
            # Salvar novas recomendações
            for rec in recommendations:
                DailyRecommendation.objects.create(
                    user=user_profile.user,
                    recommended_profile=rec['profile'],
                    compatibility_score=rec['adjusted_score'] if 'adjusted_score' in rec else rec['compatibility'],
                    reasons=", ".join(rec['reasons'])
                )
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao obter sugestões de match: {str(e)}")
            return []
    
    def update_match_status(self, user_profile, other_profile_id, status):
        """
        Atualiza o status de um match.
        
        Args:
            user_profile: Perfil do usuário
            other_profile_id: ID do outro perfil
            status: Novo status ('liked', 'rejected', 'blocked')
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            # Obter ou criar match
            match, created = Match.objects.get_or_create(
                user_a=user_profile.user,
                user_b_id=other_profile_id,
                defaults={'status': status}
            )
            
            if not created:
                # Atualizar status
                match.status = status
                match.save()
            
            # Verificar match mútuo
            is_mutual = False
            if status == 'liked':
                # Verificar se o outro usuário também deu like
                reverse_match = Match.objects.filter(
                    user_a_id=other_profile_id,
                    user_b=user_profile.user,
                    status='liked'
                ).exists()
                
                if reverse_match:
                    # Atualizar ambos os matches para mutual
                    match.is_mutual = True
                    match.save()
                    
                    Match.objects.filter(
                        user_a_id=other_profile_id,
                        user_b=user_profile.user
                    ).update(is_mutual=True)
                    
                    is_mutual = True
            
            return True, "Match atualizado com sucesso", is_mutual
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do match: {str(e)}")
            return False, f"Erro ao atualizar match: {str(e)}", False
    
    def _save_matches_to_db(self, user_profile, recommendations):
        """
        Salva recomendações no banco de dados.
        
        Args:
            user_profile: Perfil do usuário
            recommendations: Lista de recomendações
        """
        try:
            for rec in recommendations:
                other_profile = rec['profile']
                score = rec.get('adjusted_score', 
                               rec.get('compatibility', 0.5))
                
                # Apenas criar novos matches (não atualizar existentes)
                Match.objects.get_or_create(
                    user_a=user_profile.user,
                    user_b=other_profile.user,
                    defaults={
                        'compatibility_score': score * 100,  # Converter para porcentagem
                        'status': 'pending'
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao salvar matches no banco: {str(e)}")