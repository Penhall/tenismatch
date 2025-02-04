# /tenismatch/apps/tenis_admin/services/model_training_service.py
import logging
from typing import Tuple
from django.core.exceptions import ValidationError
from ..models import AIModel, Dataset
from .training_service import SneakerMatchTraining

logger = logging.getLogger(__name__)

class ModelTrainingService:
    @staticmethod
    def train_model(model_id: int, dataset_id: int) -> Tuple[bool, str]:
        """Treina um modelo de IA usando o dataset especificado"""
        try:
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            if dataset.status != 'ready':
                raise ValidationError('Dataset não está pronto para treinamento')
                
            if model.status not in ['draft']:
                raise ValidationError('Modelo não está em estado válido para treinamento')
            
            trainer = SneakerMatchTraining()
            success, message = trainer.train(dataset.file.path)
            
            if success:
                model.status = 'review'
                model.save()
                
            return success, message
            
        except Dataset.DoesNotExist:
            logger.error(f'Dataset {dataset_id} não encontrado')
            return False, 'Dataset não encontrado'
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except Exception as e:
            logger.error(f'Erro ao treinar modelo: {str(e)}')
            return False, str(e)

    @staticmethod
    def _prepare_features(df, column_mapping):
        """Prepara as features para treinamento usando o mapeamento de colunas"""
        try:
            features = []
            for column in ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']:
                if column in column_mapping:
                    mapped_column = column_mapping[column]
                    features.append(df[mapped_column].values)
                else:
                    raise ValidationError(f'Coluna {column} não encontrada no mapeamento')
            return features
        except Exception as e:
            logger.error(f'Erro ao preparar features: {str(e)}')
            raise

    @staticmethod
    def _prepare_targets(df, column_mapping):
        """Prepara os targets para treinamento usando o mapeamento de colunas"""
        try:
            target_column = column_mapping.get('target', 'match')
            if target_column in df.columns:
                return df[target_column].values
            else:
                logger.warning('Coluna target não encontrada, usando valores padrão')
                return None
        except Exception as e:
            logger.error(f'Erro ao preparar targets: {str(e)}')
            raise

    @staticmethod
    def review_model(model_id: int, approved: bool, review_notes: str = None) -> Tuple[bool, str]:
        """Processa a revisão de um modelo, aprovando ou rejeitando"""
        try:
            model = AIModel.objects.get(id=model_id)
            
            if model.status != 'review':
                raise ValidationError('Modelo não está em estado de revisão')
            
            model.status = 'approved' if approved else 'rejected'
            model.save()
            
            logger.info(f'Modelo {model_id} {"aprovado" if approved else "rejeitado"}')
            return True, 'Revisão processada com sucesso'
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except Exception as e:
            logger.error(f'Erro ao processar revisão: {str(e)}')
            return False, str(e)

    @staticmethod
    def deploy_model(model_id: int) -> Tuple[bool, str]:
        """Implanta um modelo aprovado em produção"""
        try:
            model = AIModel.objects.get(id=model_id)
            
            if model.status != 'approved':
                raise ValidationError('Apenas modelos aprovados podem ser implantados')
            
            # Aqui viria a lógica de implantação
            model.status = 'deployed'
            model.save()
            
            logger.info(f'Modelo {model_id} implantado com sucesso')
            return True, 'Modelo implantado com sucesso'
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except Exception as e:
            logger.error(f'Erro ao implantar modelo: {str(e)}')
            return False, str(e)

    @staticmethod
    def get_model_metrics(model_id: int) -> dict:
        """Retorna as métricas do modelo"""
        try:
            model = AIModel.objects.get(id=model_id)
            return model.metrics or {}
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return {}