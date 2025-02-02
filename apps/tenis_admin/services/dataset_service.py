import os
from django.conf import settings
from ..models import Dataset

class DatasetService:
    @staticmethod
    def sync_datasets(user):
        """
        Sincroniza os datasets físicos com o banco de dados
        """
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
        db_files = {os.path.basename(d.file.name) for d in db_datasets if d.file}
        
        # Remove do banco datasets que não existem mais fisicamente
        for dataset in db_datasets:
            if dataset.file and os.path.basename(dataset.file.name) not in physical_files:
                dataset.delete()
                
        # Adiciona ao banco datasets que existem fisicamente mas não no banco
        new_files = physical_files - db_files
        for file in new_files:
            file_path = os.path.join('datasets', file)
            name = os.path.splitext(file)[0]
            Dataset.objects.create(
                name=name,
                description=f'Dataset encontrado: {file}',
                file=file_path,
                uploaded_by=user  # ou um usuário padrão do sistema
            )
        
        return len(new_files)  # retorna quantidade de novos datasets encontrados
