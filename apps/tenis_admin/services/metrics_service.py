# /tenismatch/apps/tenis_admin/services/metrics_service.py
"""
Serviço para cálculo e gerenciamento de métricas dos modelos.
"""
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import AIModel
from ..utils import TimingUtil
import logging

logger = logging.getLogger(__name__)

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
            # Obter métricas, verificando se são valores válidos
            accuracy = metrics.get('accuracy', 0)
            precision = metrics.get('precision', 0)
            recall = metrics.get('recall', 0)
            f1_score = metrics.get('f1_score', 0)
            
            # Verificar se a métrica já está em porcentagem (> 1)
            # Se não estiver, converter para porcentagem
            avg_metrics['avg_accuracy'] += accuracy if accuracy > 1 else accuracy * 100
            avg_metrics['avg_precision'] += precision if precision > 1 else precision * 100
            avg_metrics['avg_recall'] += recall if recall > 1 else recall * 100
            avg_metrics['avg_f1_score'] += f1_score if f1_score > 1 else f1_score * 100
        
        n_models = len(metrics_list)
        for key in avg_metrics:
            avg_metrics[key] = round(avg_metrics[key] / n_models, 2)
            
        logger.info(f"Métricas médias calculadas: {avg_metrics}")
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
                
                # Obter métricas, verificando se são valores válidos
                accuracy = model.metrics.get('accuracy', 0)
                precision = model.metrics.get('precision', 0)
                recall = model.metrics.get('recall', 0)
                f1_score = model.metrics.get('f1_score', 0)
                
                # Verificar se a métrica já está em porcentagem (> 1)
                # Se não estiver, converter para porcentagem
                metrics_by_date[date_key]['count'] += 1
                metrics_by_date[date_key]['accuracy'] += accuracy if accuracy > 1 else accuracy * 100
                metrics_by_date[date_key]['precision'] += precision if precision > 1 else precision * 100
                metrics_by_date[date_key]['recall'] += recall if recall > 1 else recall * 100
                metrics_by_date[date_key]['f1_score'] += f1_score if f1_score > 1 else f1_score * 100
        
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
                # Dividir por contagem para calcular média e converter para valores entre 0 e 1 para o gráfico
                accuracies.append(metrics['accuracy'] / count / 100)
                precisions.append(metrics['precision'] / count / 100)
                recalls.append(metrics['recall'] / count / 100)
                f1_scores.append(metrics['f1_score'] / count / 100)
        
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
            # Converter valores para percentuais se necessário
            for key in ['accuracy', 'precision', 'recall', 'f1_score']:
                if key in metrics:
                    metrics[key] = metrics[key] if metrics[key] > 1 else round(metrics[key] * 100, 2)
            
            return metrics
        except AIModel.DoesNotExist:
            return None

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
        
        # Dados diários
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
    
    @staticmethod
    def update_all_models_metrics():
        """
        Atualiza as métricas de todos os modelos para garantir que estejam no formato de porcentagem.
        """
        models = AIModel.objects.all()
        updated_count = 0
        
        for model in models:
            if model.metrics:
                metrics_updated = False
                for key in ['accuracy', 'precision', 'recall', 'f1_score']:
                    if key in model.metrics and model.metrics[key] is not None:
                        # Se o valor for menor que 1, é uma proporção e deve ser convertida para porcentagem
                        if model.metrics[key] <= 1:
                            model.metrics[key] = model.metrics[key] * 100
                            metrics_updated = True
                
                if metrics_updated:
                    model.save()
                    updated_count += 1
        
        logger.info(f"Métricas atualizadas para {updated_count} modelos")
        return updated_count