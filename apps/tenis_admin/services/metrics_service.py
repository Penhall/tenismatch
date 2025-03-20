"""
Serviço para cálculo e gerenciamento de métricas dos modelos.
"""
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import AIModel
from ..utils import TimingUtil

class MetricsService:
    @staticmethod
    @TimingUtil.log_execution_time
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
@TimingUtil.log_execution_time
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
    
    # Agrupar modelos por data
    metrics_by_date = {}
    for model in models:
        if model.metrics:
            date_key = model.created_at.strftime('%Y-%m-%d')
            if date_key not in metrics_by_date:
                metrics_by_date[date_key] = {
                    'count': 0,
                    'accuracy': 0,
                    'precision': 0,
                    'recall': 0,
                    'f1_score': 0
                }
            
            metrics_by_date[date_key]['count'] += 1
            metrics_by_date[date_key]['accuracy'] += model.metrics.get('accuracy', 0)
            metrics_by_date[date_key]['precision'] += model.metrics.get('precision', 0)
            metrics_by_date[date_key]['recall'] += model.metrics.get('recall', 0)
            metrics_by_date[date_key]['f1_score'] += model.metrics.get('f1_score', 0)
    
    # Calcular médias e formatar dados
    dates = []
    accuracies = []
    precisions = []
    recalls = []
    f1_scores = []
    
    for date_key, metrics in sorted(metrics_by_date.items()):
        count = metrics['count']
        if count > 0:
            dates.append(date_key)
            accuracies.append(metrics['accuracy'] / count)
            precisions.append(metrics['precision'] / count)
            recalls.append(metrics['recall'] / count)
            f1_scores.append(metrics['f1_score'] / count)
    
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

# /tenismatch/apps/tenis_admin/services/metrics_service.py

@staticmethod
@TimingUtil.log_execution_time
def get_metrics_summary():
    """
    Retorna um resumo geral das métricas do sistema.
    """
    total_models = AIModel.objects.count()
    approved_models = AIModel.objects.filter(status='approved').count()
    rejected_models = AIModel.objects.filter(status='rejected').count()
    in_review = AIModel.objects.filter(status='review').count()
    
    # Calcular taxas e percentuais
    approval_rate = round((approved_models / total_models) * 100, 2) if total_models > 0 else 0
    
    # Obter métricas médias
    avg_metrics = MetricsService.calculate_average_metrics()
    
   
    daily_metrics = MetricsService.get_daily_metrics(30)  # Últimos 30 dias
    
    # Dados para tabela de modelos
    recent_models = AIModel.objects.all().order_by('-created_at')[:10]
    
    return {
        'total_models': total_models,
        'approved_models': approved_models,
        'rejected_models': rejected_models,
        'in_review': in_review,
        'approval_rate': approval_rate,
        'model_metrics': avg_metrics,
        'daily_model_metrics': daily_metrics,
        'models': recent_models
    }