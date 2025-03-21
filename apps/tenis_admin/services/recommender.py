# /tenismatch/apps/matching/services/recommender_service.py
import numpy as np
from django.db.models import Avg
import logging
import os
import joblib
from django.conf import settings
from apps.tenis_admin.services.training_service import SneakerMatchTraining

logger = logging.getLogger(__name__)

class RecommenderService:
    """
    Serviço principal para geração de recomendações baseadas em preferências de tênis.
    Utiliza o modelo treinado para predizer a compatibilidade entre usuários.
    """
    
    def __init__(self):
        self.trainer = SneakerMatchTraining()
        self.feedback_weight = 0.3  # Peso do feedback no score final
        self.model = self._load_active_model()
        
    def _load_active_model(self):
        """
        Carrega o modelo ativo de recomendação.
        Tenta carregar do diretório de produção, caso contrário usa o trainer default.
        """
        try:
            prod_model_path = os.path.join(settings.MEDIA_ROOT, 'production', 'active_model.joblib')
            if os.path.exists(prod_model_path):
                logger.info(f"Carregando modelo de produção: {prod_model_path}")
                return joblib.load(prod_model_path)
            else:
                logger.warning("Modelo de produção não encontrado. Usando modelo padrão.")
                return self.trainer.model
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            return self.trainer.model
        
    def get_recommendations(self, user_profile, limit=5):
        """
        Gera recomendações considerando histórico de feedback
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            
        Returns:
            list: Lista de recomendações ordenadas por score
        """
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
        """
        Obtém recomendações base do modelo
        
        Args:
            user_profile: Perfil do usuário
            
        Returns:
            list: Lista de recomendações base
        """
        all_profiles = self._get_candidate_profiles(user_profile)
        recommendations = []
        
        for profile in all_profiles:
            try:
                # Extrai características do tênis do usuário
                user_features = self.trainer.extract_features(user_profile.sneaker_data)
                
                # Extrai características do tênis do candidato
                profile_features = self.trainer.extract_features(profile.sneaker_data)
                
                # Calcula compatibilidade usando o modelo
                compatibility = self._predict_compatibility(user_features, profile_features)
                
                recommendations.append({
                    'profile': profile,
                    'base_score': compatibility,
                    'compatibility_reasons': self._get_compatibility_reasons(user_profile, profile)
                })
            except Exception as e:
                logger.error(f"Erro ao calcular compatibilidade: {str(e)}")
                continue
            
        return recommendations
    
    def _predict_compatibility(self, user_features, profile_features):
        """
        Prediz a compatibilidade entre dois perfis
        
        Args:
            user_features: Características do tênis do usuário
            profile_features: Características do tênis do candidato
            
        Returns:
            float: Score de compatibilidade entre 0 e 1
        """
        try:
            # Preparar features combinadas
            combined_features = np.array([
                user_features['marca_score'],
                user_features['estilo_score'],
                user_features['cores_score'],
                user_features['preco_score'],
                profile_features['marca_score'],
                profile_features['estilo_score'],
                profile_features['cores_score'],
                profile_features['preco_score'],
                # Diferenças
                abs(user_features['marca_score'] - profile_features['marca_score']),
                abs(user_features['estilo_score'] - profile_features['estilo_score']),
                abs(user_features['cores_score'] - profile_features['cores_score']),
                abs(user_features['preco_score'] - profile_features['preco_score'])
            ])
            
            # Usar modelo para predizer
            if hasattr(self.model, 'predict_proba'):
                prob = self.model.predict_proba([combined_features])
                # Retorna probabilidade da classe positiva (index 1)
                return prob[0][1] if prob.shape[1] > 1 else prob[0][0]
            else:
                # Fallback para compatibilidade baseada em heurística
                return 1.0 - (
                    abs(user_features['marca_score'] - profile_features['marca_score']) * 0.3 +
                    abs(user_features['estilo_score'] - profile_features['estilo_score']) * 0.4 +
                    abs(user_features['cores_score'] - profile_features['cores_score']) * 0.1 +
                    abs(user_features['preco_score'] - profile_features['preco_score']) * 0.2
                )
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            # Fallback para método simples
            return 0.5  # Score neutro
    
    def _adjust_with_feedback(self, recommendations, user_profile):
        """
        Ajusta scores baseado em feedback histórico
        
        Args:
            recommendations: Lista de recomendações base
            user_profile: Perfil do usuário
            
        Returns:
            list: Lista de recomendações com scores ajustados
        """
        try:
            from apps.matching.models import Match, MatchFeedback
            
            for rec in recommendations:
                profile = rec['profile']
                
                # Busca feedback histórico similar
                similar_feedback = MatchFeedback.objects.filter(
                    user=user_profile.user,
                    match__other_sneaker__style=profile.sneaker_data.get('style')
                ).aggregate(Avg('rating'))['rating__avg']
                
                if similar_feedback:
                    feedback_score = similar_feedback / 5.0  # Normaliza para 0-1
                    rec['adjusted_score'] = (
                        rec['base_score'] * (1 - self.feedback_weight) +
                        feedback_score * self.feedback_weight
                    )
                else:
                    rec['adjusted_score'] = rec['base_score']
                
        except Exception as e:
            logger.error(f"Erro ao ajustar com feedback: {str(e)}")
            # Em caso de erro, usar score base
            for rec in recommendations:
                rec['adjusted_score'] = rec['base_score']
                
        return recommendations
    
    def _get_candidate_profiles(self, user_profile):
        """
        Filtra perfis candidatos baseado em critérios
        
        Args:
            user_profile: Perfil do usuário
            
        Returns:
            QuerySet: Perfis candidatos filtrados
        """
        try:
            from apps.users.models import UserProfile
            from apps.matching.models import Match
            
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
        except Exception as e:
            logger.error(f"Erro ao obter perfis candidatos: {str(e)}")
            # Em caso de erro, retorna queryset vazio
            from apps.users.models import UserProfile
            return UserProfile.objects.none()
    
    def _get_compatibility_reasons(self, user_profile, other_profile):
        """
        Gera razões textuais para a compatibilidade entre perfis
        
        Args:
            user_profile: Perfil do usuário
            other_profile: Perfil do outro usuário
            
        Returns:
            list: Lista de razões para a compatibilidade
        """
        try:
            reasons = []
            user_data = user_profile.sneaker_data
            other_data = other_profile.sneaker_data
            
            # Verifica marca
            if user_data.get('tenis_marca') == other_data.get('tenis_marca'):
                reasons.append(f"Vocês têm preferência pela mesma marca: {user_data.get('tenis_marca')}")
            
            # Verifica estilo
            if user_data.get('tenis_estilo') == other_data.get('tenis_estilo'):
                reasons.append(f"Vocês compartilham do mesmo estilo: {user_data.get('tenis_estilo')}")
            
            # Verifica preço
            user_price = float(user_data.get('tenis_preco', 0))
            other_price = float(other_data.get('tenis_preco', 0))
            if abs(user_price - other_price) < 100:
                reasons.append("Vocês têm gostos semelhantes em termos de valor de tênis")
            
            # Se não encontrou razões específicas
            if not reasons:
                reasons.append("Vocês têm estilos complementares que podem combinar bem")
                
            return reasons
            
        except Exception as e:
            logger.error(f"Erro ao gerar razões de compatibilidade: {str(e)}")
            return ["Vocês possuem compatibilidade baseada em seus estilos de tênis"]