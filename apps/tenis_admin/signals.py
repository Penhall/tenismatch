# /tenismatch/apps/tenis_admin/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import AIModel, Dataset
import logging
import threading

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

def _background_model_processing(model_id, status):
    """Executa tarefas demoradas em background"""
    try:
        model = AIModel.objects.get(id=model_id)
        
        if status == 'approved':
            # Importar aqui para evitar importação circular
            from .services import ModelDeploymentService
            try:
                ModelDeploymentService.deploy_model(model_id)
                logger.info(f'Modelo {model_id} implantado com sucesso')
            except Exception as e:
                logger.error(f'Erro ao implantar modelo {model_id}: {str(e)}')
            
        # Enviar email de notificação
        if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
            subject = 'Modelo Aprovado' if status == 'approved' else 'Modelo Rejeitado'
            message = f'Seu modelo {model.name} v{model.version} foi {"aprovado" if status == "approved" else "rejeitado"}.'
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [model.created_by.email],
                )
                logger.info(f'Email enviado para {model.created_by.email}')
            except Exception as e:
                logger.error(f'Erro ao enviar email para {model.created_by.email}: {str(e)}')
    except Exception as e:
        logger.error(f'Erro no processamento em background do modelo {model_id}: {str(e)}')

@receiver(post_save, sender=AIModel)
def handle_model_status_change(sender, instance, **kwargs):
    """Gerencia mudanças de status em modelos de IA"""
    try:
        if instance.status in ['approved', 'rejected']:
            # Executar tarefas demoradas em uma thread separada
            logger.info(f'Iniciando processamento em background para modelo {instance.id}')
            thread = threading.Thread(
                target=_background_model_processing,
                args=(instance.id, instance.status)
            )
            thread.daemon = True  # Garante que a thread não bloqueie o encerramento do programa
            thread.start()
    except Exception as e:
        logger.error(f'Erro ao iniciar processamento em background do modelo {instance.id}: {str(e)}')