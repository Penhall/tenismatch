# /tenismatch/apps/users/models.py
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('GERENTE', 'Gerente'),
        ('ANALISTA', 'Analista'),
        ('USUARIO', 'Usuário Regular'),  # Adicionando papel para usuários comuns
    )
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    matches_remaining = models.IntegerField(default=3)  # Para usuários free
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, db_index=True)  # Adicionado índice
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USUARIO', db_index=True)  # Alterado para 'USUARIO'
    
    def has_premium_access(self):
        if not self.is_premium:
            return False
        return self.premium_until is None or self.premium_until > timezone.now()

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
        
    def is_analyst(self):
        # Implementação com cache
        cache_key = f'user_{self.id}_is_analyst'
        result = cache.get(cache_key)
        if result is None:
            result = self.role == 'ANALISTA'
            cache.set(cache_key, result, 3600)  # Cache por 1 hora
        return result

    def is_manager(self):
        # Implementação com cache
        cache_key = f'user_{self.id}_is_manager'
        result = cache.get(cache_key)
        if result is None:
            result = self.role == 'GERENTE'
            cache.set(cache_key, result, 3600)  # Cache por 1 hora
        return result

    def invalidate_role_cache(self):
        # Método para invalidar o cache quando o papel do usuário muda
        cache.delete(f'user_{self.id}_is_analyst')
        cache.delete(f'user_{self.id}_is_manager')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Se não é novo, verificar se o papel mudou
        if not is_new:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.role != self.role:
                    self.invalidate_role_cache()
            except User.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"New user created: {self.username}, role: {self.role}, is_approved: {self.is_approved}")
        else:
            logger.info(f"User updated: {self.username}, role: {self.role}, is_approved: {self.is_approved}")

    class Meta:
        db_table = 'auth_user'