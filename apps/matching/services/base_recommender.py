# /tenismatch/apps/matching/services/base_recommender.py
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseRecommender(ABC):
    """
    Classe base abstrata para implementações de recomendação.
    Define a interface comum que todos os recomendadores devem implementar.
    """
    
    @abstractmethod
    def get_recommendations(self, user_profile, limit=5):
        """
        Gera recomendações para um usuário.
        
        Args:
            user_profile: Perfil do usuário para o qual gerar recomendações
            limit: Número máximo de recomendações a retornar
            
        Returns:
            list: Lista de perfis recomendados
        """
        pass
    
    @abstractmethod
    def calculate_compatibility(self, user_profile, other_profile):
        """
        Calcula a compatibilidade entre dois perfis.
        
        Args:
            user_profile: Perfil do usuário atual
            other_profile: Perfil do outro usuário
            
        Returns:
            float: Score de compatibilidade (0-1)
        """
        pass
    
    @abstractmethod
    def get_compatibility_reasons(self, user_profile, other_profile):
        """
        Gera razões para a compatibilidade entre dois perfis.
        
        Args:
            user_profile: Perfil do usuário atual
            other_profile: Perfil do outro usuário
            
        Returns:
            list: Lista de razões textuais
        """
        pass
    
    def filter_candidates(self, user_profile):
        """
        Filtra candidatos para recomendação.
        
        Args:
            user_profile: Perfil do usuário atual
            
        Returns:
            QuerySet: QuerySet de perfis candidatos
        """
        try:
            from apps.users.models import UserProfile
            from ..models import Match
            
            # Exclui usuários já rejeitados ou bloqueados
            excluded_users = Match.objects.filter(
                user_a=user_profile.user,
                status__in=['rejected', 'blocked']
            ).values_list('user_b_id', flat=True)
            
            # Aplicar filtros básicos
            candidates = UserProfile.objects.exclude(
                user__id__in=excluded_users
            ).exclude(
                user=user_profile.user
            )
            
            # Aplicar filtros adicionais se disponíveis
            if hasattr(user_profile, 'preferences') and user_profile.preferences:
                # Preferências de idade (exemplo)
                if hasattr(user_profile.preferences, 'min_age') and user_profile.preferences.min_age:
                    candidates = candidates.filter(age__gte=user_profile.preferences.min_age)
                
                if hasattr(user_profile.preferences, 'max_age') and user_profile.preferences.max_age:
                    candidates = candidates.filter(age__lte=user_profile.preferences.max_age)
                
                # Preferências de localização (exemplo)
                if hasattr(user_profile.preferences, 'location_radius') and user_profile.preferences.location_radius:
                    # Implementar filtro de distância
                    # Esta é uma simplificação; um sistema real usaria um cálculo geoespacial
                    if hasattr(user_profile, 'location'):
                        candidates = candidates.filter(location=user_profile.location)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Erro ao filtrar candidatos: {str(e)}")
            # Em caso de erro, retornar QuerySet vazio
            from apps.users.models import UserProfile
            return UserProfile.objects.none()