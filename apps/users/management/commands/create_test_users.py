from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = 'Creates or updates test users for the TenisMatch application'

    def create_or_update_user(self, username, email, password, role, is_approved):
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'role': role,
                'is_approved': is_approved
            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created {role} user: {username}'))
        else:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {role} user: {username}'))
        return user

    def handle(self, *args, **options):
        # Create or update Analyst user
        self.create_or_update_user('analyst', 'analyst@example.com', 'senha123', 'ANALISTA', False)

        # Create or update Manager user
        self.create_or_update_user('manager', 'manager@example.com', 'senha123', 'GERENTE', True)

        # Create or update approved Analyst
        self.create_or_update_user('approved_analyst', 'approved_analyst@example.com', 'senha123', 'ANALISTA', True)
