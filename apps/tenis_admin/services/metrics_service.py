
from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.matching.models import Match, MatchFeedback

class MetricsService:
    @staticmethod
    def get_feedback_metrics(days=30):
        """Calcula métricas de feedback dos últimos X dias"""
        period_start = timezone.now() - timedelta(days=days)
        
        # Métricas gerais
        general_metrics = MatchFeedback.objects.filter(
            created_at__gte=period_start
        ).aggregate(
            avg_rating=Avg('rating'),
            total_feedback=Count('id'),
            positive_feedback=Count('id', filter=F('rating__gte=4'))
        )
        
        # Calcula taxa de feedback positivo
        if general_metrics['total_feedback'] > 0:
            general_metrics['positive_rate'] = (
                general_metrics['positive_feedback'] / 
                general_metrics['total_feedback']
            ) * 100
        else:
            general_metrics['positive_rate'] = 0
            
        return general_metrics
    
    @staticmethod
    def get_match_quality_metrics(days=30):
        """Analisa qualidade dos matches gerados"""
        period_start = timezone.now() - timedelta(days=days)
        
        # Métricas de matches
        match_metrics = Match.objects.filter(
            created_at__gte=period_start
        ).aggregate(
            total_matches=Count('id'),
            mutual_matches=Count('id', filter=F('is_mutual=True')),
            avg_compatibility=Avg('compatibility_score')
        )
        
        # Taxa de matches mútuos
        if match_metrics['total_matches'] > 0:
            match_metrics['mutual_rate'] = (
                match_metrics['mutual_matches'] / 
                match_metrics['total_matches']
            ) * 100
        else:
            match_metrics['mutual_rate'] = 0
            
        return match_metrics
    
    @staticmethod
    def get_style_performance():
        """Analisa performance por estilo de tênis"""
        style_metrics = MatchFeedback.objects.values(
            'match__other_sneaker__style'
        ).annotate(
            avg_rating=Avg('rating'),
            total_matches=Count('id'),
            success_rate=ExpressionWrapper(
                Count('id', filter=F('rating__gte=4')) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('-avg_rating')
        
        return list(style_metrics)
    
    @staticmethod
    def get_daily_metrics(days=30):
        """Retorna métricas diárias para gráficos"""
        period_start = timezone.now() - timedelta(days=days)
        
        daily_metrics = MatchFeedback.objects.filter(
            created_at__gte=period_start
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            avg_rating=Avg('rating'),
            total_feedback=Count('id'),
            positive_rate=ExpressionWrapper(
                Count('id', filter=F('rating__gte=4')) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('date')
        
        return list(daily_metrics)