# /tenismatch/apps/users/models.py 
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('GERENTE', 'Gerente'),
        ('ANALISTA', 'Analista'),
    )
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    matches_remaining = models.IntegerField(default=3)  # Para usuários free
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ANALISTA')
    
    def has_premium_access(self):
        if not self.is_premium:
            return False
        return self.premium_until is None or self.premium_until > timezone.now()

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def is_analyst(self):
        return self.role == 'ANALISTA'

    def is_manager(self):
        return self.role == 'GERENTE'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"New user created: {self.username}, role: {self.role}, is_approved: {self.is_approved}")
        else:
            logger.info(f"User updated: {self.username}, role: {self.role}, is_approved: {self.is_approved}")

    class Meta:
        db_table = 'users'
