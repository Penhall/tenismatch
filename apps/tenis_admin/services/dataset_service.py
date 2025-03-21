# /tenismatch/apps/tenis_admin/services/dataset_service.py
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import Dataset, ColumnMapping
import pandas as pd
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()

class DatasetService:
    @staticmethod
    def sync_datasets():
        """
        Sincroniza os datasets físicos com o banco de dados
        Não requer um usuário específico, usa o primeiro superusuário disponível
        """
        try:
            # Encontrar um usuário admin para associar datasets sem dono
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()  # Fallback para qualquer usuário
            
            if not admin_user:
                logger.error("Não foi possível encontrar um usuário para associar aos datasets")
                return 0
                
            # Caminho para diretório de datasets
            dataset_dir = os.path.join(settings.MEDIA_ROOT, 'datasets')
            
            # Cria diretório se não existir
            if not os.path.exists(dataset_dir):
                os.makedirs(dataset_dir)
                
            # Lista arquivos físicos
            physical_files = set()
            for file in os.listdir(dataset_dir):
                if file.endswith(('.csv', '.xlsx', '.xls')):
                    physical_files.add(file)
                    
            # Lista datasets no banco
            db_datasets = Dataset.objects.all()
            
            # Para cada dataset no banco, verifica se o arquivo físico existe
            for dataset in db_datasets:
                if not dataset.file:
                    continue  # Pula datasets sem arquivo
                    
                file_name = os.path.basename(dataset.file.name)
                file_path = os.path.join(dataset_dir, file_name)
                
                # Se arquivo não existe, marca com status de erro
                if file_name not in physical_files:
                    logger.warning(f"Arquivo não encontrado para dataset {dataset.id}: {file_name}")
                    dataset.status = 'processing'  # Marca para reprocessamento
                    dataset.save()
                    continue
                
                # Se o dataset não está pronto, tenta processá-lo
                if dataset.status != 'ready':
                    DatasetService.process_dataset(dataset.id)
                    
            # Adiciona ao banco datasets que existem fisicamente mas não no banco
            db_files = {os.path.basename(d.file.name) for d in db_datasets if d.file}
            new_files = physical_files - db_files
            
            new_datasets_count = 0
            for file in new_files:
                file_path = os.path.join('datasets', file)
                name = os.path.splitext(file)[0]
                
                # Cria novo dataset
                Dataset.objects.create(
                    name=f"Importado: {name}",
                    description=f'Dataset importado automaticamente: {file}',
                    file=file_path,
                    uploaded_by=admin_user,
                    uploaded_at=timezone.now()
                )
                new_datasets_count += 1
                
            logger.info(f"Sincronização concluída: {new_datasets_count} novos datasets encontrados")
            return new_datasets_count
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar datasets: {str(e)}")
            return 0

    @staticmethod
    def process_dataset(dataset_id):
        """Processa um dataset após upload"""
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            
            if not dataset.file:
                logger.error(f"Dataset {dataset_id} não possui arquivo associado")
                return False
                
            # Verifica se o arquivo existe
            file_path = dataset.file.path
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado para dataset {dataset_id}: {file_path}")
                return False
                
            # Determina o tipo de arquivo
            ext = os.path.splitext(file_path)[1].lower()
            
            # Lê o arquivo de acordo com a extensão
            try:
                if ext == '.csv':
                    df = pd.read_csv(file_path)
                elif ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path)
                else:
                    logger.error(f"Tipo de arquivo não suportado para dataset {dataset_id}: {ext}")
                    return False
            except Exception as e:
                logger.error(f"Erro ao ler arquivo do dataset {dataset_id}: {str(e)}")
                return False
            
            # Salva estatísticas básicas
            dataset.records_count = len(df)
            dataset.stats = {
                'columns': list(df.columns),
                'rows': len(df),
                'sample': df.head(5).to_dict(orient='records')
            }
            
            # Verifica se tem as colunas necessárias - agora opcional
            required_columns = set(['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco'])
            current_columns = set(df.columns)
            
            # Se todas as colunas necessárias existem, marca como pronto
            # Caso contrário, marca para mapeamento
            if required_columns.issubset(current_columns):
                dataset.status = 'ready'
                dataset.is_processed = True
            else:
                dataset.status = 'mapping'
                dataset.stats['missing_columns'] = list(required_columns - current_columns)
            
            dataset.save()
            
            logger.info(f'Dataset {dataset_id} processado com sucesso. Status: {dataset.status}')
            return True
            
        except Dataset.DoesNotExist:
            logger.error(f'Dataset {dataset_id} não encontrado')
            return False
        except Exception as e:
            logger.error(f'Erro ao processar dataset {dataset_id}: {str(e)}')
            return False
            
    @staticmethod
    def apply_mapping(dataset_id, mapping):
        """
        Aplica o mapeamento de colunas ao dataset
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            
            if not dataset.file:
                logger.error(f"Dataset {dataset_id} não possui arquivo associado")
                return False, "Dataset não possui arquivo associado"
                
            # Verifica se o arquivo existe
            file_path = dataset.file.path
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado para dataset {dataset_id}: {file_path}")
                return False, "Arquivo não encontrado"
            
            # Verifica se o mapeamento tem todas as colunas necessárias
            required_columns = ['tenis_marca', 'tenis_estilo', 'tenis_cores', 'tenis_preco']
            for col in required_columns:
                if col not in mapping:
                    return False, f"Mapeamento não contém a coluna '{col}'"
            
            # Salva o mapeamento
            column_mapping, created = ColumnMapping.objects.get_or_create(dataset=dataset)
            column_mapping.mapping = mapping
            column_mapping.is_mapped = True
            column_mapping.save()
            
            # Atualiza o status do dataset
            dataset.status = 'ready'
            dataset.is_processed = True
            dataset.save()
            
            logger.info(f"Mapeamento aplicado com sucesso para dataset {dataset_id}")
            return True, "Mapeamento aplicado com sucesso"
            
        except Dataset.DoesNotExist:
            logger.error(f"Dataset {dataset_id} não encontrado")
            return False, "Dataset não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao aplicar mapeamento para dataset {dataset_id}: {str(e)}")
            return False, f"Erro ao aplicar mapeamento: {str(e)}"