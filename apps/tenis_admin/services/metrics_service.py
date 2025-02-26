"""
Serviço para cálculo e gerenciamento de métricas dos modelos.
"""
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import AIModel

class MetricsService:
    @staticmethod
    def calculate_average_metrics():
        """
        Calcula as métricas médias de todos os modelos aprovados.
        """
        approved_models = AIModel.objects.filter(status='approved')
        metrics_list = [model.metrics for model in approved_models if model.metrics]
        
        if not metrics_list:
            return {
                'avg_accuracy': 0,
                'avg_precision': 0,
                'avg_recall': 0,
                'avg_f1_score': 0
            }
        
        avg_metrics = {
            'avg_accuracy': 0,
            'avg_precision': 0,
            'avg_recall': 0,
            'avg_f1_score': 0
        }
        
        for metrics in metrics_list:
            avg_metrics['avg_accuracy'] += metrics.get('accuracy', 0)
            avg_metrics['avg_precision'] += metrics.get('precision', 0)
            avg_metrics['avg_recall'] += metrics.get('recall', 0)
            avg_metrics['avg_f1_score'] += metrics.get('f1_score', 0)
        
        n_models = len(metrics_list)
        for key in avg_metrics:
            avg_metrics[key] = round((avg_metrics[key] / n_models) * 100, 2)
            
        return avg_metrics

    @staticmethod
    def get_daily_metrics(days=30):
        """
        Retorna métricas diárias dos últimos X dias.
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        models = AIModel.objects.filter(
            created_at__range=(start_date, end_date),
            status='approved'
        ).order_by('created_at')
        
        dates = []
        accuracies = []
        precisions = []
        recalls = []
        f1_scores = []
        
        current_date = start_date
        while current_date <= end_date:
            day_models = [m for m in models if m.created_at.date() == current_date.date()]
            
            if day_models:
                day_metrics = []
                for model in day_models:
                    if model.metrics:
                        day_metrics.append({
                            'accuracy': model.metrics.get('accuracy', 0),
                            'precision': model.metrics.get('precision', 0),
                            'recall': model.metrics.get('recall', 0),
                            'f1_score': model.metrics.get('f1_score', 0)
                        })
                
                if day_metrics:
                    dates.append(current_date.strftime('%Y-%m-%d'))
                    accuracies.append(np.mean([m['accuracy'] for m in day_metrics]))
                    precisions.append(np.mean([m['precision'] for m in day_metrics]))
                    recalls.append(np.mean([m['recall'] for m in day_metrics]))
                    f1_scores.append(np.mean([m['f1_score'] for m in day_metrics]))
            
            current_date += timedelta(days=1)
        
        return {
            'dates': dates,
            'accuracies': accuracies,
            'precisions': precisions,
            'recalls': recalls,
            'f1_scores': f1_scores
        }

    @staticmethod
    def get_model_metrics(model_id):
        """
        Retorna métricas detalhadas de um modelo específico.
        """
        try:
            model = AIModel.objects.get(id=model_id)
            if not model.metrics:
                return None
            
            metrics = model.metrics.copy()
            # Converter valores para percentuais
            for key in ['accuracy', 'precision', 'recall', 'f1_score']:
                if key in metrics:
                    metrics[key] = round(metrics[key] * 100, 2)
            
            return metrics
        except AIModel.DoesNotExist:
            return None

    @staticmethod
    def get_metrics_summary():
        """
        Retorna um resumo geral das métricas do sistema.
        """
        total_models = AIModel.objects.count()
        approved_models = AIModel.objects.filter(status='approved').count()
        rejected_models = AIModel.objects.filter(status='rejected').count()
        in_review = AIModel.objects.filter(status='review').count()
        
        avg_metrics = MetricsService.calculate_average_metrics()
        
        return {
            'total_models': total_models,
            'approved_models': approved_models,
            'rejected_models': rejected_models,
            'in_review': in_review,
            'avg_metrics': avg_metrics
        }
