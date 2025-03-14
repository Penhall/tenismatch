# /tenismatch/apps/tenis_admin/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import AIModel, Dataset
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Dataset)
def process_dataset(sender, instance, created, **kwargs):
    """Processa o dataset após o upload"""
    if created:
        logger.info(f'Novo dataset criado: {instance.id}')
        try:
            from .services.dataset_service import DatasetService
            result = DatasetService.process_dataset(instance.id)
            logger.info(f'Processamento do dataset {instance.id}: {"Sucesso" if result else "Falha"}')
        except Exception as e:
            logger.error(f'Erro ao processar dataset {instance.id}: {str(e)}')

@receiver(post_save, sender=AIModel)
def handle_model_status_change(sender, instance, **kwargs):
    """Gerencia mudanças de status em modelos de IA"""
    try:
        if instance.status == 'approved':
            from .services import ModelDeploymentService
            ModelDeploymentService.deploy_model(instance.id)
            
            # Notificar criador do modelo se email estiver configurado
            if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
                try:
                    send_mail(
                        'Modelo Aprovado',
                        f'Seu modelo {instance.name} v{instance.version} foi aprovado.',
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.created_by.email],
                    )
                except Exception as e:
                    logger.error(f'Erro ao enviar email para {instance.created_by.email}: {str(e)}')
                    
        elif instance.status == 'rejected':
            # Notificar criador do modelo se email estiver configurado
            if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
                try:
                    send_mail(
                        'Modelo Rejeitado',
                        f'Seu modelo {instance.name} v{instance.version} foi rejeitado.',
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.created_by.email],
                    )
                except Exception as e:
                    logger.error(f'Erro ao enviar email para {instance.created_by.email}: {str(e)}')
    except Exception as e:
        logger.error(f'Erro ao processar mudança de status do modelo {instance.id}: {str(e)}')