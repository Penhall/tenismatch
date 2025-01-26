# /tenismatch/apps/matching/services/data_processor.py 
from django.db.models import Avg, Count
from ..models import Match, SneakerProfile

class DataProcessor:
    @staticmethod
    def get_match_statistics(user):
        return Match.objects.filter(user_a=user).aggregate(
            avg_score=Avg('compatibility_score'),
            total_matches=Count('id'),
            mutual_matches=Count('id', filter={'is_mutual': True})
        )

    @staticmethod
    def get_style_distribution():
        return SneakerProfile.objects.values('style').annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def get_user_matching_history(user, limit=10):
        return Match.objects.filter(user_a=user).order_by(
            '-matched_at'
        )[:limit]

    @staticmethod
    def process_sneaker_data(sneaker_profile):
        data = {
            'style_vector': [0] * len(SneakerProfile.STYLE_CHOICES),
            'color_vector': [0] * len(SneakerProfile.COLOR_CHOICES),
            'price_normalized': sneaker_profile.price_range / 5.0,
        }
        
        # One-hot encoding para estilo
        style_idx = next(i for i, (code, _) in enumerate(SneakerProfile.STYLE_CHOICES) 
                        if code == sneaker_profile.style)
        data['style_vector'][style_idx] = 1
        
        # One-hot encoding para cor
        color_idx = next(i for i, (code, _) in enumerate(SneakerProfile.COLOR_CHOICES) 
                        if code == sneaker_profile.color)
        data['color_vector'][color_idx] = 1
        
        return data