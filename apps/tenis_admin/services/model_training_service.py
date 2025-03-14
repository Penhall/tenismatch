import logging
import os
import pandas as pd
import numpy as np
import joblib
from typing import Tuple
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ..models import AIModel, Dataset, ColumnMapping

logger = logging.getLogger(__name__)

class ModelTrainingService:
    @staticmethod
    def train_model(model_id: int, dataset_id: int) -> Tuple[bool, str]:
        """
        Treina um modelo de IA usando o dataset especificado.
        
        Args:
            model_id (int): ID do modelo a ser treinado
            dataset_id (int): ID do dataset a ser usado para treinamento
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Buscar o modelo e o dataset
            model = AIModel.objects.get(id=model_id)
            dataset = Dataset.objects.get(id=dataset_id)
            
            # Verificar se o dataset está pronto
            if dataset.status != 'ready':
                raise ValidationError('Dataset não está pronto para treinamento')
                
            # Verificar se o modelo está em estado válido para treinamento
            if model.status not in ['draft']:
                raise ValidationError('Modelo não está em estado válido para treinamento')
            
            # Alterar o status para 'training'
            model.status = 'training'
            model.save()
            
            # Carregar o dataset
            df = pd.read_csv(dataset.file.path)
            
            # Verificar se existem mapeamentos de colunas
            try:
                column_mapping = ColumnMapping.objects.get(dataset=dataset)
                if column_mapping.is_mapped:
                    # Aplicar mapeamento de colunas
                    mapping = column_mapping.mapping
                    for target_col, source_col in mapping.items():
                        if source_col in df.columns:
                            df[target_col] = df[source_col]
            except ColumnMapping.DoesNotExist:
                # Se não existir mapeamento, verificar se as colunas necessárias existem
                required_cols = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
                for col in required_cols:
                    if col not in df.columns:
                        raise ValidationError(f'Coluna {col} não encontrada no dataset')
            
            # Preparar os dados para treinamento
            X, y = ModelTrainingService._prepare_data(df)
            
            # Dividir entre treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Criar e treinar o modelo
            clf = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Treinar o modelo
            clf.fit(X_train, y_train)
            
            # Avaliar o modelo
            y_pred = clf.predict(X_test)
            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
            }
            
            # Garantir que o diretório para salvar o modelo existe
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'models'), exist_ok=True)
            
            # Salvar o modelo treinado
            model_path = os.path.join(settings.MEDIA_ROOT, 'models', f'model_{model_id}.joblib')
            joblib.dump(clf, model_path)
            
            # Atualizar o modelo no banco
            model.metrics = metrics
            model.status = 'review'  # Alterar para revisão após treinamento
            model.model_file = f'models/model_{model_id}.joblib'
            model.training_completed_at = timezone.now()
            model.save()
            
            logger.info(f"Modelo {model_id} treinado com sucesso. Métricas: {metrics}")
            return True, f"Modelo treinado com sucesso. Acurácia: {metrics['accuracy']:.2f}"
            
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
            # Em caso de erro, atualizar o status do modelo
            try:
                model = AIModel.objects.get(id=model_id)
                model.status = 'draft'  # Voltar para draft em caso de erro
                model.save()
            except:
                pass
            return False, f'Erro ao treinar modelo: {str(e)}'
    
    @staticmethod
    def _prepare_data(df):
        """
        Processa o DataFrame e prepara para treinamento.
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados do dataset
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Features (X) e targets (y)
        """
        # Processar as colunas de características
        X = ModelTrainingService._prepare_features(df)
        
        # Criar valores de target a partir dos dados
        # Aqui estamos simulando uma classificação binária (match/no match)
        # Em um sistema real, isso seria derivado de dados reais de interação
        y = ModelTrainingService._prepare_targets(df)
        
        return X, y
    
    @staticmethod
    def _prepare_features(df):
        """
        Prepara as features para treinamento.
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados do dataset
            
        Returns:
            np.ndarray: Features processadas
        """
        # Selecionar colunas relevantes
        feature_cols = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
        
        # Certificar que todas as colunas existem
        for col in feature_cols:
            if col not in df.columns:
                raise ValidationError(f'Coluna {col} não encontrada no dataset')
        
        # Realizar codificação das categorias
        X = pd.DataFrame()
        
        # Codificar marca
        le_marca = LabelEncoder()
        X['marca_encoded'] = le_marca.fit_transform(df['tenis_marca'])
        
        # Codificar estilo
        le_estilo = LabelEncoder()
        X['estilo_encoded'] = le_estilo.fit_transform(df['tenis_estilo'])
        
        # Codificar cores
        le_cores = LabelEncoder()
        X['cores_encoded'] = le_cores.fit_transform(df['tenis_cores'])
        
        # Normalizar preço
        X['preco_norm'] = df['tenis_preco'] / df['tenis_preco'].max()
        
        # Retornar como array numpy
        return X.values
    
    @staticmethod
    def _prepare_targets(df):
        """
        Prepara os valores alvo (y) para treinamento.
        
        Args:
            df (pandas.DataFrame): DataFrame com os dados do dataset
            
        Returns:
            np.ndarray: Valores alvo
        """
        # Em um caso real, isso seria baseado em dados de compatibilidade.
        # Como estamos simulando, vamos criar uma regra simples baseada nas características:
        
        # Criar um array para valores de compatibilidade
        compatibility = np.zeros(len(df))
        
        # Regras simplificadas para match (podem ser adaptadas conforme necessário)
        # Tênis da mesma marca e estilo têm maior chance de match
        le_marca = LabelEncoder()
        marca_encoded = le_marca.fit_transform(df['tenis_marca'])
        
        le_estilo = LabelEncoder()
        estilo_encoded = le_estilo.fit_transform(df['tenis_estilo'])
        
        # Cores complementares têm chance média de match
        le_cores = LabelEncoder()
        cores_encoded = le_cores.fit_transform(df['tenis_cores'])
        
        # Preço similar tem pequena influência no match
        preco_norm = df['tenis_preco'] / df['tenis_preco'].max()
        
        # Combinar as características para criar um score
        for i in range(len(df)):
            # Score baseado nas características (0-1)
            score = (
                np.random.normal(0.5, 0.15) +  # Base aleatória para simular variabilidade
                0.2 * (marca_encoded[i] % 2) +  # Marca influencia 20%
                0.3 * (estilo_encoded[i] % 3) / 3 +  # Estilo influencia 30%
                0.1 * (cores_encoded[i] % 5) / 5 +  # Cor influencia 10%
                0.1 * preco_norm[i]  # Preço influencia 10%
            )
            
            # Normalizar para 0-1
            score = max(0, min(1, score))
            
            # Classificar como match (1) ou não match (0)
            compatibility[i] = 1 if score > 0.5 else 0
        
        return compatibility

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
            
            # TODO: Implementar a lógica de implantação do modelo
            # Por exemplo, copiar o modelo para diretório de produção ou atualizar configuração
            
            # Atualizar o status do modelo
            model.status = 'deployed'
            model.save()
            
            return True, "Modelo implantado com sucesso"
            
        except AIModel.DoesNotExist:
            logger.error(f'Modelo {model_id} não encontrado')
            return False, 'Modelo não encontrado'
            
        except Exception as e:
            logger.error(f'Erro ao implantar modelo: {str(e)}', exc_info=True)
            return False, f'Erro ao implantar modelo: {str(e)}'