import numpy as np
from django.db.models import Avg
from apps.matching.models import Match, MatchFeedback
from .training_service import SneakerMatchTraining

class EnhancedRecommender:
    def __init__(self):
        self.trainer = SneakerMatchTraining()
        self.feedback_weight = 0.3  # Peso do feedback no score final
        
    def get_recommendations(self, user_profile, limit=5):
        """Gera recomendações considerando histórico de feedback"""
        base_recommendations = self._get_base_recommendations(user_profile)
        feedback_adjusted = self._adjust_with_feedback(base_recommendations, user_profile)
        
        # Ordena por score ajustado
        recommendations = sorted(
            feedback_adjusted, 
            key=lambda x: x['adjusted_score'], 
            reverse=True
        )
        
        return recommendations[:limit]
    
    def _get_base_recommendations(self, user_profile):
        """Obtem recomendações base do modelo"""
        all_profiles = self._get_candidate_profiles(user_profile)
        recommendations = []
        
        for profile in all_profiles:
            compatibility = self.trainer.predict_match(
                user_profile.sneaker_data,
                profile.sneaker_data
            )
            
            recommendations.append({
                'profile': profile,
                'base_score': compatibility
            })
            
        return recommendations
    
    def _adjust_with_feedback(self, recommendations, user_profile):
        """Ajusta scores baseado em feedback histórico"""
        for rec in recommendations:
            profile = rec['profile']
            
            # Busca feedback histórico similar
            similar_feedback = MatchFeedback.objects.filter(
                user=user_profile.user,
                match__other_sneaker__style=profile.sneaker_profile.style
            ).aggregate(Avg('rating'))['rating__avg']
            
            if similar_feedback:
                feedback_score = similar_feedback / 5.0  # Normaliza para 0-1
                rec['adjusted_score'] = (
                    rec['base_score'] * (1 - self.feedback_weight) +
                    feedback_score * self.feedback_weight
                )
            else:
                rec['adjusted_score'] = rec['base_score']
            
        return recommendations
    
    def _get_candidate_profiles(self, user_profile):
        """Filtra perfis candidatos baseado em critérios"""
        from apps.users.models import UserProfile
        
        # Exclui usuários já rejeitados ou bloqueados
        excluded_users = Match.objects.filter(
            user=user_profile.user,
            status__in=['rejected', 'blocked']
        ).values_list('other_user_id', flat=True)
        
        return UserProfile.objects.exclude(
            user__id__in=excluded_users
        ).exclude(
            user=user_profile.user
        )