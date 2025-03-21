# /tenismatch/apps/matching/services/basic_recommender.py
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .base_recommender import BaseRecommender
from .match_statistics_service import MatchStatisticsService

logger = logging.getLogger(__name__)

class BasicRecommender(BaseRecommender):
    """
    Implementação básica de recomendação usando similaridade de cosseno
    e regras heurísticas, sem uso de modelo de ML.
    """
    
    def __init__(self):
        self.style_weights = {
            'ESP': {'adventurous': 0.8, 'athletic': 0.7, 'casual': 0.3},
            'CAS': {'casual': 0.9, 'social': 0.6, 'practical': 0.7},
            'VIN': {'artistic': 0.8, 'alternative': 0.7, 'classic': 0.6},
            'SOC': {'elegant': 0.8, 'social': 0.9, 'formal': 0.7},
            'FAS': {'trendy': 0.9, 'creative': 0.8, 'bold': 0.7}
        }
        
        self.brand_compatibility = {
            'NIK': {'NIK': 0.9, 'ADI': 0.6, 'PUM': 0.5, 'REB': 0.5, 'NB': 0.4},
            'ADI': {'NIK': 0.6, 'ADI': 0.9, 'PUM': 0.6, 'REB': 0.5, 'NB': 0.4},
            'PUM': {'NIK': 0.5, 'ADI': 0.6, 'PUM': 0.9, 'REB': 0.6, 'NB': 0.5},
            'REB': {'NIK': 0.5, 'ADI': 0.5, 'PUM': 0.6, 'REB': 0.9, 'NB': 0.6},
            'NB': {'NIK': 0.4, 'ADI': 0.4, 'PUM': 0.5, 'REB': 0.6, 'NB': 0.9}
        }
    
    def get_recommendations(self, user_profile, limit=5):
        """
        Gera recomendações para um usuário baseadas em similaridade de estilo.
        
        Args:
            user_profile: Perfil do usuário
            limit: Número máximo de recomendações
            
        Returns:
            list: Lista de recomendações ordenadas por compatibilidade
        """
        try:
            # Filtrar candidatos
            candidates = self.filter_candidates(user_profile)
            recommendations = []
            
            # Calcular vetor de personalidade do usuário atual
            user_vector = self.calculate_personality_vector(user_profile.sneaker_profile)
            
            for candidate in candidates:
                # Verificar se tem perfil de tênis
                if not hasattr(candidate, 'sneaker_profile'):
                    continue
                
                # Calcular score de compatibilidade
                compatibility = self.calculate_compatibility(
                    user_profile.sneaker_profile, 
                    candidate.sneaker_profile
                )
                
                # Razões para compatibilidade
                reasons = self.get_compatibility_reasons(
                    user_profile.sneaker_profile,
                    candidate.sneaker_profile
                )
                
                recommendations.append({
                    'profile': candidate,
                    'compatibility': compatibility,
                    'reasons': reasons
                })
            
            # Ordenar por compatibilidade
            recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações básicas: {str(e)}")
            return []
    
    def calculate_compatibility(self, user_profile, other_profile):
        """
        Calcula compatibilidade entre dois perfis baseada em similaridade de cosseno.
        
        Args:
            user_profile: Perfil de tênis do usuário
            other_profile: Perfil de tênis do outro usuário
            
        Returns:
            float: Score de compatibilidade entre 0 e 1
        """
        try:
            # Calcular vetores de personalidade
            user_vector = self.calculate_personality_vector(user_profile)
            other_vector = self.calculate_personality_vector(other_profile)
            
            # Calcular similaridade de cosseno
            similarity = cosine_similarity([user_vector], [other_vector])[0][0]
            
            # Adicionar componente de marca
            brand_factor = 0.0
            if hasattr(user_profile, 'brand') and hasattr(other_profile, 'brand'):
                brand_code_user = user_profile.brand[:3].upper()
                brand_code_other = other_profile.brand[:3].upper()
                
                if (brand_code_user in self.brand_compatibility and 
                    brand_code_other in self.brand_compatibility[brand_code_user]):
                    brand_factor = self.brand_compatibility[brand_code_user][brand_code_other]
            
            # Fator de estilo (mesmos estilos têm alta compatibilidade)
            style_factor = 1.0 if user_profile.style == other_profile.style else 0.5
            
            # Fator de preço (preços similares têm alta compatibilidade)
            price_diff = abs(user_profile.price_range - other_profile.price_range)
            price_factor = 1.0 - (price_diff / 5.0)  # Normalizado para range 0-1
            
            # Combinar fatores
            final_score = (
                similarity * 0.4 +  # Personalidade: 40%
                brand_factor * 0.2 +  # Marca: 20%
                style_factor * 0.3 +  # Estilo: 30%
                price_factor * 0.1    # Preço: 10%
            )
            
            return min(1.0, max(0.0, final_score))  # Garantir que está entre 0 e 1
            
        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade: {str(e)}")
            return 0.5  # Valor neutro em caso de erro
    
    def get_compatibility_reasons(self, user_profile, other_profile):
        """
        Gera razões para a compatibilidade entre dois perfis.
        
        Args:
            user_profile: Perfil de tênis do usuário
            other_profile: Perfil de tênis do outro usuário
            
        Returns:
            list: Lista de razões textuais
        """
        try:
            reasons = []
            
            # Verificar estilo
            if user_profile.style == other_profile.style:
                reasons.append(f"Vocês têm preferência pelo mesmo estilo de tênis: {self._get_style_name(user_profile.style)}")
            else:
                reasons.append("Seus estilos de tênis se complementam")
            
            # Verificar marca
            if hasattr(user_profile, 'brand') and hasattr(other_profile, 'brand'):
                if user_profile.brand == other_profile.brand:
                    reasons.append(f"Vocês preferem a mesma marca: {user_profile.brand}")
            
            # Verificar preço
            price_diff = abs(user_profile.price_range - other_profile.price_range)
            if price_diff <= 1:
                reasons.append("Vocês valorizam tênis na mesma faixa de preço")
            
            # Se não encontrou razões específicas
            if not reasons:
                reasons.append("Vocês têm estilos complementares que podem combinar bem")
                
            return reasons
            
        except Exception as e:
            logger.error(f"Erro ao gerar razões de compatibilidade: {str(e)}")
            return ["Vocês possuem compatibilidade baseada em seus estilos de tênis"]
    
    def calculate_personality_vector(self, sneaker_profile):
        """
        Calcula um vetor de "personalidade" baseado no perfil de tênis.
        
        Args:
            sneaker_profile: Perfil de tênis
            
        Returns:
            np.ndarray: Vetor de personalidade normalizado
        """
        try:
            # Vetor de personalidade com 8 dimensões
            # [adventurous, social, practical, artistic, classic, elegant, formal, trendy]
            personality = np.zeros(8)
            
            # Ajustar baseado no estilo
            style_code = sneaker_profile.style[:3].upper()
            if style_code in self.style_weights:
                for idx, (trait, weight) in enumerate(self.style_weights[style_code].items()):
                    trait_idx = self._get_trait_idx(trait)
                    personality[trait_idx] = weight
            
            # Normalizar o vetor
            if np.sum(personality) > 0:
                personality = personality / np.sum(personality)
                
            return personality
            
        except Exception as e:
            logger.error(f"Erro ao calcular vetor de personalidade: {str(e)}")
            return np.ones(8) / 8  # Vetor uniforme em caso de erro
    
    def _get_trait_idx(self, trait):
        """
        Mapeia nome de traço para índice no vetor.
        
        Args:
            trait: Nome do traço de personalidade
            
        Returns:
            int: Índice no vetor
        """
        traits = [
            'adventurous', 'social', 'practical', 'artistic', 
            'classic', 'elegant', 'formal', 'trendy'
        ]
        
        try:
            return traits.index(trait)
        except ValueError:
            return 0
    
    def _get_style_name(self, style_code):
        """
        Obtém o nome legível do estilo a partir do código.
        
        Args:
            style_code: Código do estilo
            
        Returns:
            str: Nome legível do estilo
        """
        style_names = {
            'ESP': 'Esportivo',
            'CAS': 'Casual',
            'VIN': 'Vintage',
            'SOC': 'Social',
            'FAS': 'Fashion'
        }
        
        return style_names.get(style_code, style_code)