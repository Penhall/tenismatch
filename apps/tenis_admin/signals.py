# /tenismatch/apps/tenis_admin/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import AIModel, Dataset
from .services import DatasetService, ModelDeploymentService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Dataset)
def process_dataset(sender, instance, created, **kwargs):
    if created:
        DatasetService.process_dataset(instance.id)

@receiver(post_save, sender=AIModel)
def handle_model_status_change(sender, instance, **kwargs):
    if instance.status == 'approved':
        ModelDeploymentService.deploy_model(instance.id)
        # Notificar criador do modelo
        send_mail(
            'Modelo Aprovado',
            f'Seu modelo {instance.name} v{instance.version} foi aprovado.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.created_by.email],
        )
    elif instance.status == 'rejected':
        # Notificar criador do modelo
        send_mail(
            'Modelo Rejeitado',
            f'Seu modelo {instance.name} v{instance.version} foi rejeitado.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.created_by.email],
        )

@receiver(post_save, sender=Dataset)
def process_dataset(sender, instance, created, **kwargs):
    """Processa o dataset após o upload"""
    if created:
        logger.info(f'Novo dataset criado: {instance.id}')
        DatasetService.process_dataset(instance.id)