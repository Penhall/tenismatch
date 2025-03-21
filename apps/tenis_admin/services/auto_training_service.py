# /tenismatch/apps/tenis_admin/services/auto_training_service.py
import logging
import pandas as pd
import numpy as np
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .training_service import SneakerMatchTraining
from .model_training_service import ModelTrainingService
from ..models import AIModel, Dataset
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class AutoTrainingService:
    """
    Serviço para treinamento automático de modelos baseado em novos feedbacks.
    Monitora o sistema e inicia treinamentos quando necessário.
    """
    
    def __init__(self):
        self.trainer = SneakerMatchTraining()
        self.min_feedback_threshold = 100  # Mínimo de feedbacks para retreinar
        self.min_days_between_training = 7  # Mínimo de dias entre treinos
        
    def check_and_train(self):
        """
        Verifica se é necessário retreinar e executa se necessário
        
        Returns:
            AIModel or None: Novo modelo criado ou None se não retrainado
        """
        try:
            if self._should_retrain():
                logger.info("Iniciando treinamento automático baseado em novos feedbacks")
                return self._perform_training()
            else:
                logger.info("Não é necessário retreinamento neste momento")
                return None
        except Exception as e:
            logger.error(f"Erro ao verificar necessidade de retreinamento: {str(e)}")
            return None
        
    def _should_retrain(self):
        """
        Verifica se modelo deve ser retreinado
        
        Returns:
            bool: True se modelo deve ser retreinado, False caso contrário
        """
        try:
            # Verifica último modelo aprovado
            last_model = AIModel.objects.filter(
                status__in=['approved', 'deployed']
            ).order_by('-created_at').first()
            
            # Definir data de referência
            reference_date = last_model.created_at if last_model else timezone.now() - timedelta(days=365)
            
            # Verificar tempo desde último treinamento
            if last_model and (timezone.now() - reference_date).days < self.min_days_between_training:
                logger.info(f"Retreinamento não necessário: último modelo foi criado há menos de {self.min_days_between_training} dias")
                return False
                
            # Contar novos feedbacks desde último treinamento
            try:
                from apps.matching.models import MatchFeedback
                
                new_feedback_count = MatchFeedback.objects.filter(
                    created_at__gt=reference_date
                ).count()
                
                logger.info(f"Novos feedbacks desde último treinamento: {new_feedback_count}")
                return new_feedback_count >= self.min_feedback_threshold
                
            except ImportError:
                logger.warning("Modelo MatchFeedback não disponível, usando critério de tempo apenas")
                return (timezone.now() - reference_date).days >= 30  # Fallback: treinar a cada 30 dias
                
        except Exception as e:
            logger.error(f"Erro ao verificar necessidade de retreinamento: {str(e)}")
            return False
        
    def _perform_training(self):
        """
        Executa treinamento automático
        
        Returns:
            AIModel: Novo modelo criado
        """
        try:
            # Criar ou obter dataset para treinamento
            dataset = self._prepare_training_dataset()
            
            if not dataset:
                logger.error("Não foi possível preparar dataset para treinamento automático")
                return None
            
            # Criar modelo
            model = AIModel.objects.create(
                name=f'AutoTrained_{timezone.now().strftime("%Y%m%d")}',
                version=f'auto-{timezone.now().strftime("%Y%m%d-%H%M")}',
                description='Modelo treinado automaticamente com base em feedbacks recentes',
                dataset=dataset,
                created_by=self._get_system_user(),
                status='draft'
            )
            
            # Treinar modelo
            success, result = ModelTrainingService.train_model_async(model.id, dataset.id)
            
            if not success:
                logger.error(f"Falha ao iniciar treinamento automático: {result}")
                model.delete()
                return None
                
            logger.info(f"Treinamento automático iniciado com sucesso: Modelo ID {model.id}")
            return model
            
        except Exception as e:
            logger.error(f"Erro ao realizar treinamento automático: {str(e)}")
            return None
        
    def _prepare_training_dataset(self):
        """
        Prepara dataset para treinamento automático
        
        Returns:
            Dataset: Dataset preparado para treinamento
        """
        try:
            # Tentativa 1: Usar dataset existente com status 'ready'
            ready_dataset = Dataset.objects.filter(status='ready').order_by('-created_at').first()
            
            if ready_dataset:
                logger.info(f"Usando dataset existente ID {ready_dataset.id} para treinamento automático")
                return ready_dataset
                
            # Tentativa 2: Gerar novo dataset com dados de feedback
            dataset_path = self._create_feedback_dataset()
            
            if dataset_path:
                # Criar novo dataset no sistema
                new_dataset = Dataset.objects.create(
                    name=f'AutoGenerated_{timezone.now().strftime("%Y%m%d")}',
                    description='Dataset gerado automaticamente com feedbacks de usuários',
                    file=dataset_path.replace(settings.MEDIA_ROOT + '/', ''),
                    uploaded_by=self._get_system_user(),
                    status='ready',
                    is_processed=True
                )
                
                logger.info(f"Criado novo dataset ID {new_dataset.id} para treinamento automático")
                return new_dataset
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao preparar dataset para treinamento: {str(e)}")
            return None
    
    def _create_feedback_dataset(self):
        """
        Cria dataset baseado em feedbacks de usuários
        
        Returns:
            str: Caminho para o arquivo de dataset criado ou None
        """
        try:
            # Coletar dados de feedbacks
            training_data = self._collect_training_data()
            
            if not training_data or len(training_data) < 50:  # Mínimo de 50 exemplos
                logger.warning("Dados de feedback insuficientes para gerar dataset")
                return None
                
            # Converter para DataFrame
            df = pd.DataFrame(training_data)
            
            # Salvar em arquivo
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'datasets'), exist_ok=True)
            file_path = os.path.join(settings.MEDIA_ROOT, 'datasets', f'auto_feedback_{timezone.now().strftime("%Y%m%d")}.csv')
            df.to_csv(file_path, index=False)
            
            logger.info(f"Dataset de feedback criado com {len(df)} exemplos: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Erro ao criar dataset de feedback: {str(e)}")
            return None
        
    def _collect_training_data(self):
        """
        Coleta dados para treino do modelo a partir de feedbacks de usuários
        
        Returns:
            list: Lista de dados para treino
        """
        try:
            from apps.matching.models import Match, MatchFeedback
            training_data = []
            
            # Coleta matches com feedback
            matches_with_feedback = MatchFeedback.objects.select_related(
                'match', 'match__user_a__sneakerprofile', 'match__user_b__sneakerprofile'
            )
            
            for feedback in matches_with_feedback:
                match = feedback.match
                
                # Verificar se os perfis de tênis existem
                if not hasattr(match.user_a, 'sneakerprofile') or not hasattr(match.user_b, 'sneakerprofile'):
                    continue
                
                user_sneaker = match.user_a.sneakerprofile
                other_sneaker = match.user_b.sneakerprofile
                
                # Dados do tênis do usuário
                user_data = {
                    'tenis_marca': user_sneaker.brand,
                    'tenis_estilo': user_sneaker.style,
                    'tenis_cores': user_sneaker.color,
                    'tenis_preco': user_sneaker.price_range
                }
                
                # Dados do tênis do match
                other_data = {
                    'tenis_marca': other_sneaker.brand,
                    'tenis_estilo': other_sneaker.style,
                    'tenis_cores': other_sneaker.color,
                    'tenis_preco': other_sneaker.price_range
                }
                
                # Considera match bem sucedido se feedback rating >= 4
                label = 1 if feedback.rating >= 4 else 0
                
                # Combinar dados
                combined_data = {
                    'tenis_marca': user_data['tenis_marca'],
                    'tenis_estilo': user_data['tenis_estilo'],
                    'tenis_cores': user_data['tenis_cores'],
                    'tenis_preco': user_data['tenis_preco'],
                    'other_marca': other_data['tenis_marca'],
                    'other_estilo': other_data['tenis_estilo'],
                    'other_cores': other_data['tenis_cores'],
                    'other_preco': other_data['tenis_preco'],
                    'label': label
                }
                
                training_data.append(combined_data)
                
            return training_data
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados de treinamento: {str(e)}")
            return []
    
    def _get_system_user(self):
        """
        Obtém usuário do sistema para associar aos modelos/datasets automatizados
        
        Returns:
            User: Objeto de usuário do sistema
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Busca admin ou primeiro usuário
        system_user = User.objects.filter(is_superuser=True).first()
        if not system_user:
            system_user = User.objects.first()
            
        return system_user