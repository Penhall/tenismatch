# /tenismatch/apps/tenis_admin/services/model_training_service.py
import logging
import os
import pandas as pd
import numpy as np
import joblib
import threading
import time
import re
from typing import Tuple
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ..models import AIModel, Dataset, ColumnMapping
from .training_service import SneakerMatchTraining

logger = logging.getLogger(__name__)

class ModelTrainingService:
    @staticmethod
    def train_model_async(model_id: int, dataset_id: int) -> Tuple[bool, str]:
        """
        Inicia o treinamento de um modelo em uma thread separada
        
        Args:
            model_id (int): ID do modelo a ser treinado
            dataset_id (int): ID do dataset a ser usado para treinamento
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Verificar se o modelo e o dataset existem
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            if not dataset:
                return False, "Dataset não encontrado"
            
            # Iniciar thread para treinamento
            thread = threading.Thread(
                target=lambda: ModelTrainingService._train_task(model_id, dataset_id)
            )
            thread.daemon = True
            thread.start()
            
            return True, "Treinamento iniciado em segundo plano"
            
        except AIModel.DoesNotExist:
            logger.error(f"Modelo {model_id} não encontrado")
            return False, "Modelo não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao iniciar treinamento assíncrono: {str(e)}")
            return False, f"Erro ao iniciar treinamento: {str(e)}"

    @staticmethod
    def _train_task(model_id: int, dataset_id: int):
        """
        Função para treinar modelo em uma thread separada
        
        Args:
            model_id (int): ID do modelo a ser treinado
            dataset_id (int): ID do dataset a ser usado para treinamento
        """
        try:
            model = AIModel.objects.get(id=model_id)
            model.training_status = 'processing'
            model.training_started_at = timezone.now()
            model.training_message = 'Iniciando treinamento...'
            model.training_progress = 0
            model.save()
            
            # Etapa 1: Carregando dados (0-20%)
            model.training_progress = 10
            model.training_message = 'Carregando dataset...'
            model.save()
            
            # Etapa 2: Preparando dados (20-40%)
            model.training_progress = 30
            model.training_message = 'Preparando dados para treinamento...'
            model.save()
            
            # Etapa 3: Treinando modelo (40-80%)
            model.training_progress = 50
            model.training_message = 'Treinando modelo...'
            model.save()
            
            # Chamar o treinamento real
            success, result = ModelTrainingService.train_model(model_id, dataset_id)
            
            # Etapa 4: Finalizando (80-100%)
            if success:
                model.training_progress = 100
                model.training_status = 'completed'
                model.training_message = 'Treinamento concluído com sucesso!'
                model.status = 'review'  # Status original do modelo
                if isinstance(result, dict):
                    model.metrics = result
            else:
                model.training_progress = 100
                model.training_status = 'failed'
                model.training_message = f'Falha no treinamento: {result}'
                model.status = 'draft'  # Volta para draft em caso de falha
            
            model.training_completed_at = timezone.now()
            model.save()
            
        except Exception as e:
            logger.error(f"Erro no treinamento assíncrono: {str(e)}")
            try:
                model = AIModel.objects.get(id=model_id)
                model.training_status = 'failed'
                model.training_message = f'Erro: {str(e)}'
                model.training_completed_at = timezone.now()
                model.status = 'draft'  # Volta para draft em caso de erro
                model.save()
            except Exception as inner_e:
                logger.error(f"Erro ao atualizar status do modelo após falha: {str(inner_e)}")

    @staticmethod
    def train_model(model_id: int, dataset_id: int) -> Tuple[bool, str]:
        """
        Treina um modelo de IA usando o dataset especificado.
        
        Args:
            model_id (int): ID do modelo a ser treinado
            dataset_id (int): ID do dataset a ser usado para treinamento
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem ou métricas)
        """
        try:
            # Buscar o modelo e o dataset
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            # Verificar se o dataset está pronto
            if dataset.status != 'ready':
                raise ValidationError(f'Dataset não está pronto para treinamento. Status: {dataset.status}')
                
            # Verificar se o modelo está em estado válido para treinamento
            if model.status not in ['draft', 'rejected']:
                raise ValidationError(f'Modelo não está em estado válido para treinamento. Status: {model.status}')
            
            # Verificar se o arquivo do dataset existe
            if not dataset.file or not os.path.exists(dataset.file.path):
                raise ValidationError('Arquivo do dataset não encontrado')
            
            # Usar o SneakerMatchTraining para treinar
            trainer = SneakerMatchTraining()
            success, result = trainer.train(dataset.file.path)
            
            if success and isinstance(result, dict):
                # Atualizar métricas do modelo
                model.metrics = result
                
                # Criar nome de arquivo seguro para Windows
                # Extrair apenas o nome do arquivo do caminho completo
                base_filename = os.path.basename(dataset.file.path)
                
                # Limpar o nome do arquivo para garantir compatibilidade com sistemas de arquivos
                safe_filename = re.sub(r'[\\/*?:"<>|]', "_", base_filename)
                model_filename = f'model_{safe_filename}.joblib'
                model_file_path = f'models/{model_filename}'
                
                # Salvar referência ao arquivo do modelo
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'models', model_filename)):
                    model.model_file = model_file_path
                
                # Atualizar status para revisão
                model.status = 'review'
                model.save()
                
                logger.info(f"Modelo {model_id} treinado com sucesso. Métricas: {result}")
                return True, result
            
            logger.error(f"Falha ao treinar modelo {model_id}: {result}")
            return False, result if isinstance(result, str) else "Erro desconhecido no treinamento"
            
        except Dataset.DoesNotExist:
            logger.error(f'Dataset {dataset_id} não encontrado')
            return False, 'Dataset não encontrado'
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except ValidationError as e:
            logger.error(f'Erro de validação: {str(e)}')
            return False, str(e)
            
        except Exception as e:
            logger.error(f'Erro ao treinar modelo: {str(e)}', exc_info=True)
            return False, f'Erro ao treinar modelo: {str(e)}'
    
    @staticmethod
    def review_model(model_id: int, approved: bool, review_notes: str = None) -> Tuple[bool, str]:
        """
        Processa a revisão de um modelo, aprovando ou rejeitando
        
        Args:
            model_id (int): ID do modelo a ser revisado
            approved (bool): True para aprovar, False para rejeitar
            review_notes (str, optional): Observações da revisão
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            model = AIModel.objects.get(id=model_id)
            
            # Verificar se o modelo está em estado de revisão
            if model.status != 'review':
                logger.error(f"Modelo {model_id} não está em estado de revisão. Status: {model.status}")
                return False, f"Modelo não está em estado de revisão. Status: {model.status}"
            
            # Atualizar status baseado na decisão
            model.status = 'approved' if approved else 'rejected'
            
            # Adicionar notas de revisão, se fornecidas
            if review_notes:
                if not model.metrics:
                    model.metrics = {}
                model.metrics['review_notes'] = review_notes
            
            model.save()
            
            logger.info(f"Modelo {model_id} {'aprovado' if approved else 'rejeitado'} com sucesso")
            return True, "Modelo revisado com sucesso"
            
        except AIModel.DoesNotExist:
            logger.error(f"Modelo {model_id} não encontrado")
            return False, "Modelo não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao processar revisão do modelo {model_id}: {str(e)}")
            return False, f"Erro ao processar revisão: {str(e)}"

    @staticmethod
    def deploy_model(model_id: int) -> Tuple[bool, str]:
        """
        Implanta um modelo de IA em produção.
        
        Args:
            model_id (int): ID do modelo a ser implantado
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            model = AIModel.objects.get(id=model_id)
            
            # Verificar se o modelo está aprovado
            if model.status != 'approved':
                return False, "Apenas modelos aprovados podem ser implantados"
            
            # Verificar se o modelo tem arquivo
            if not model.model_file:
                return False, "Arquivo do modelo não encontrado"
            
            file_path = os.path.join(settings.MEDIA_ROOT, str(model.model_file))
            if not os.path.exists(file_path):
                return False, "Arquivo físico do modelo não encontrado"
            
            # Criar diretório de produção se não existir
            prod_dir = os.path.join(settings.MEDIA_ROOT, 'production')
            os.makedirs(prod_dir, exist_ok=True)
            
            # Copiar modelo para diretório de produção
            import shutil
            prod_file = os.path.join(prod_dir, f"active_model.joblib")
            shutil.copy2(file_path, prod_file)
            
            # Criar arquivo de configuração com metadados
            import json
            config = {
                'model_id': model.id,
                'name': model.name,
                'version': model.version,
                'deployed_at': timezone.now().isoformat(),
                'metrics': model.metrics
            }
            
            with open(os.path.join(prod_dir, 'config.json'), 'w') as f:
                json.dump(config, f, indent=2)
            
            # Atualizar o status do modelo
            model.status = 'deployed'
            model.save()
            
            logger.info(f"Modelo {model_id} implantado com sucesso")
            return True, "Modelo implantado com sucesso"
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except Exception as e:
            logger.error(f'Erro ao implantar modelo: {str(e)}', exc_info=True)
            return False, f'Erro ao implantar modelo: {str(e)}'