# /tenismatch/apps/users/models.py 
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    matches_remaining = models.IntegerField(default=3)  # Para usuários free
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def has_premium_access(self):
        if not self.is_premium:
            return False
        return self.premium_until is None or self.premium_until > timezone.now()

    class Meta:
        db_table = 'users'