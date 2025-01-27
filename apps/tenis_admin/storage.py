from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

class ModelStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=os.path.join(settings.MEDIA_ROOT, 'models'))

    def get_valid_name(self, name):
        """
        Retorna um nome válido para o arquivo do modelo
        """
        base, ext = os.path.splitext(name)
        return f"{base}_{settings.MODEL_VERSION}{ext}"

class DatasetStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=os.path.join(settings.MEDIA_ROOT, 'datasets'))

    def get_available_name(self, name, max_length=None):
        """
        Renomeia arquivos caso já existam
        """
        if self.exists(name):
            base, ext = os.path.splitext(name)
            counter = 1
            while self.exists(f"{base}_{counter}{ext}"):
                counter += 1
            name = f"{base}_{counter}{ext}"
        return name