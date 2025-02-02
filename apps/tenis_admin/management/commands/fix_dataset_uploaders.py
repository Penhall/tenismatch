from django.core.management.base import BaseCommand
from apps.tenis_admin.models import Dataset
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Atribui um usuário padrão para datasets com uploaded_by=None'

    def handle(self, *args, **options):
        default_user = User.objects.first()  # Ou outro critério para escolher o usuário
        if not default_user:
            self.stdout.write(self.style.ERROR('Nenhum usuário encontrado.'))
            return

        datasets_sem_usuario = Dataset.objects.filter(uploaded_by__isnull=True)
        count = datasets_sem_usuario.update(uploaded_by=default_user)
        self.stdout.write(self.style.SUCCESS(f'Atribuídos {count} datasets ao usuário {default_user.username}'))
