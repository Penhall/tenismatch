# /tenismatch/apps/tenis_admin/apps.py
from django.apps import AppConfig

class TenisAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenis_admin'
    
    def ready(self):
        # Importar signals
        import apps.tenis_admin.signals
        
        # Não podemos sincronizar datasets aqui diretamente
        # porque pode causar problemas durante a inicialização Django
        # Em vez disso, usamos um sinal post_migrate
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate)
        def sync_datasets_after_migrate(sender, **kwargs):
            # Apenas executar para o app correto
            if sender.name == self.name:
                try:
                    from .services.dataset_service import DatasetService
                    DatasetService.sync_datasets()
                except Exception as e:
                    print(f"Erro ao sincronizar datasets: {e}")