# /tenismatch/apps/profiles/apps.py
from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    
    def ready(self):
        # Importar signals para registrá-los
        import apps.profiles.signals