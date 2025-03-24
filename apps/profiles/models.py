# /tenismatch/apps/profiles/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class UserProfile(models.Model):
    USER_TYPES = (
        ('athlete', 'Atleta'),
        ('fashion', 'Moda'),
        ('casual', 'Casual'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='casual')
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    shoe_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    preferred_brands = models.JSONField(default=list)
    style_preferences = models.JSONField(default=dict)
    compatibility_scores = models.JSONField(default=dict)
    fashion_specialization = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    profile_version = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Garantir que preferred_brands e style_preferences não sejam None
        if self.preferred_brands is None:
            self.preferred_brands = []
            
        if self.style_preferences is None:
            self.style_preferences = {}
            
        # Incrementar a versão do perfil quando atualizado
        if not is_new:
            self.profile_version += 1
        
        # Salvar o perfil atual
        super().save(*args, **kwargs)
        
        # Criar um registro histórico após salvar
        if not is_new or kwargs.get('force_history', False):
            # Coletar dados para o histórico, excluindo campos específicos
            profile_data = {
                'id': self.id,
                'user': self.user_id,
                'user_type': self.user_type,
                'bio': self.bio,
                'location': self.location,
                'shoe_size': self.shoe_size,
                'preferred_brands': self.preferred_brands,
                'style_preferences': self.style_preferences,
                'compatibility_scores': self.compatibility_scores,
                'fashion_specialization': self.fashion_specialization,
                'experience_years': self.experience_years,
                'profile_version': self.profile_version,
            }
            
            # Criar um novo registro histórico
            ProfileHistory.objects.create(
                profile=self,
                data=profile_data
            )
            
            logger.info(f"Criado histórico para o perfil do usuário {self.user.username}, versão {self.profile_version}")


class ProfileHistory(models.Model):
    """
    Modelo para armazenar o histórico de versões de perfis de usuário.
    Cada alteração no perfil cria um novo registro histórico em vez de
    armazenar dados aninhados no próprio perfil.
    """
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='history')
    data = models.JSONField()  # Armazena apenas os dados dessa versão
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Histórico de Perfil'
        verbose_name_plural = 'Históricos de Perfil'
    
    def __str__(self):
        return f"Histórico do perfil {self.profile_id} em {self.timestamp}"