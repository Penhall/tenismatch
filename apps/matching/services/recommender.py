import joblib
from apps.tenis_admin.models import AIModel
from ...tenis_admin.services.training_service import SneakerMatchTraining

class TenisMatchRecommender:
    def __init__(self):
        # Carrega o modelo mais recente aprovado
        self.model = self._load_latest_model()
        self.trainer = SneakerMatchTraining()

    def _load_latest_model(self):
        latest_model = AIModel.objects.filter(
            status='approved'
        ).order_by('-created_at').first()
        
        if latest_model and latest_model.model_file:
            return joblib.load(latest_model.model_file.path)
        return None

    def get_recommendations(self, user_profile, limit=5):
        if not self.model:
            # Fallback para recomendações básicas se não houver modelo
            return self._get_basic_recommendations(user_profile, limit)

        # Extrai características do usuário
        user_features = self.trainer.extract_features(user_profile.sneaker_data)
        
        # Busca usuários compatíveis
        all_profiles = UserProfile.objects.exclude(user=user_profile.user)
        recommendations = []
        
        for profile in all_profiles:
            profile_features = self.trainer.extract_features(profile.sneaker_data)
            score = self.trainer.calculate_compatibility(user_features, profile_features)
            recommendations.append((profile, score))
        
        # Ordena por compatibilidade
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]

    def _get_basic_recommendations(self, user_profile, limit=5):
        # Lógica básica de recomendação sem ML
        return UserProfile.objects.filter(
            sneaker_profile__style=user_profile.sneaker_profile.style
        ).exclude(user=user_profile.user)[:limit]
