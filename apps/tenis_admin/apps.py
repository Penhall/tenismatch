# /tenismatch/apps/tenis_admin/apps.py 
from django.apps import AppConfig

class TenisAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenis_admin'
    verbose_name = 'Administração TenisMatch'

    def ready(self):
        import apps.tenis_admin.signals
