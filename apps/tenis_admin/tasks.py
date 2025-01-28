
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .services.auto_training import AutoTrainingService
from .services.metrics_service import MetricsService

User = get_user_model()

@shared_task
def check_and_train_model():
    """Task periódica para verificar necessidade de treino"""
    trainer = AutoTrainingService()
    new_model = trainer.check_and_train()
    
    if new_model:
        # Notifica gerentes sobre novo modelo para revisão
        managers = User.objects.filter(groups__name='Manager')
        
        for manager in managers:
            send_mail(
                'Novo Modelo Disponível para Revisão',
                f'Um novo modelo ({new_model.name}) foi treinado automaticamente e necessita sua revisão.',
                settings.DEFAULT_FROM_EMAIL,
                [manager.email],
                fail_silently=True
            )

@shared_task
def generate_weekly_report():
    """Gera e envia relatório semanal de métricas"""
    metrics_service = MetricsService()
    
    # Coleta métricas
    feedback_metrics = metrics_service.get_feedback_metrics(days=7)
    match_metrics = metrics_service.get_match_quality_metrics(days=7)
    style_metrics = metrics_service.get_style_performance()
    
    # Formata relatório
    report = f"""
    Relatório Semanal - TenisMatch

    Métricas de Feedback:
    - Avaliação Média: {feedback_metrics['avg_rating']:.2f}/5.0
    - Taxa de Feedback Positivo: {feedback_metrics['positive_rate']:.1f}%
    - Total de Feedbacks: {feedback_metrics['total_feedback']}

    Métricas de Matches:
    - Taxa de Matches Mútuos: {match_metrics['mutual_rate']:.1f}%
    - Compatibilidade Média: {match_metrics['avg_compatibility']:.1f}%
    - Total de Matches: {match_metrics['total_matches']}

    Top 3 Estilos:
    {_format_top_styles(style_metrics[:3])}
    """
    
    # Envia para gerentes
    managers = User.objects.filter(groups__name='Manager')
    
    for manager in managers:
        send_mail(
            'Relatório Semanal - TenisMatch',
            report,
            settings.DEFAULT_FROM_EMAIL,
            [manager.email],
            fail_silently=True
        )

def _format_top_styles(styles):
    """Formata top estilos para o relatório"""
    formatted = []
    for i, style in enumerate(styles, 1):
        formatted.append(
            f"{i}. {style['style_display']}: "
            f"{style['success_rate']:.1f}% taxa de sucesso "
            f"({style['avg_rating']:.1f}/5.0 avaliação média)"
        )
    return '\n'.join(formatted)