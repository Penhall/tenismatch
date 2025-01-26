# /tenismatch/apps/matching/services/recommender.py 
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ..models import SneakerProfile, Match

class TenisMatchRecommender:
    def __init__(self):
        self.style_weights = {
            'ESP': {'adventurous': 0.8, 'social': 0.6},
            'CAS': {'social': 0.7, 'practical': 0.8},
            'VIN': {'creative': 0.9, 'individual': 0.7},
            'SOC': {'sophisticated': 0.8, 'social': 0.7},
            'FAS': {'trendy': 0.9, 'expressive': 0.8}
        }
        
    def calculate_personality_vector(self, sneaker_profile):
        personality = np.zeros(8)  # 8 dimensões de personalidade
        
        # Ajusta vetor baseado no estilo do tênis
        if sneaker_profile.style in self.style_weights:
            for idx, (trait, weight) in enumerate(self.style_weights[sneaker_profile.style].items()):
                personality[idx] = weight
                
        # Normaliza o vetor
        if np.sum(personality) > 0:
            personality = personality / np.sum(personality)
            
        return personality
        
    def get_recommendations(self, user_profile, limit=5):
        # Obtém todos os perfis exceto o do usuário atual
        all_profiles = SneakerProfile.objects.exclude(user=user_profile.user)
        
        # Calcula vetor de personalidade do usuário atual
        user_vector = self.calculate_personality_vector(user_profile)
        
        matches = []
        for profile in all_profiles:
            profile_vector = self.calculate_personality_vector(profile)
            
            # Calcula similaridade
            similarity = cosine_similarity([user_vector], [profile_vector])[0][0]
            
            # Converte para porcentagem
            compatibility = round(similarity * 100, 2)
            
            # Cria ou atualiza match
            match, created = Match.objects.update_or_create(
                user_a=user_profile.user,
                user_b=profile.user,
                defaults={'compatibility_score': compatibility}
            )
            
            matches.append((match, compatibility))
            
        # Ordena por compatibilidade e retorna os top N
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]

    def get_common_interests(self, user_a_profile, user_b_profile):
        # Implementar lógica de interesses comuns baseada nos perfis
        interests = set()
        
        # Adiciona interesses baseados no estilo do tênis
        if user_a_profile.style == user_b_profile.style:
            interests.add('Estilo de Tênis')
            
        # Adiciona interesses baseados na marca
        if user_a_profile.brand == user_b_profile.brand:
            interests.add('Marca Favorita')
            
        return list(interests)