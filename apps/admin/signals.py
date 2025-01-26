# /tenismatch/apps/admin/signals.py 
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AIModel, Dataset
from .services import DatasetService, ModelTrainingService, ModelDeploymentService

@receiver(post_save, sender=Dataset)
def process_dataset(sender, instance, created, **kwargs):
    if created:
        DatasetService.process_dataset(instance.id)

@receiver(post_save, sender=AIModel)
def handle_model_status_change(sender, instance, **kwargs):
    if instance.status == 'approved':
        ModelDeploymentService.deploy_model(instance.id)
    elif instance.status == 'review':
        # Notificar gerentes sobre novo modelo para revisão
        pass