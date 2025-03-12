from django.db import models
from django.conf import settings
from django.utils import timezone
from django.forms.models import model_to_dict

class UserProfile(models.Model):
    USER_TYPES = (
        ('athlete', 'Atleta'),
        ('analyst', 'Analista de Moda'),
        ('enthusiast', 'Entusiasta de Tênis'),
        ('admin', 'Administrador')
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='athlete'
    )
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Preferências de estilo
    shoe_size = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )
    preferred_brands = models.JSONField(default=list)
    style_preferences = models.JSONField(
        default=dict,
        help_text="Preferências de estilo e personalização"
    )
    
    # Dados profissionais (para analistas)
    fashion_specialization = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    experience_years = models.IntegerField(default=0)
    
    # Metadados técnicos
    profile_version = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)
    historical_data = models.JSONField(
        default=list,
        help_text="Histórico de alterações do perfil"
    )
    
    # Sistema de compatibilidade
    compatibility_scores = models.JSONField(
        default=dict,
        help_text="Scores de compatibilidade com outros usuários"
    )
    
    class Meta:
        verbose_name = "Perfil Consolidado"
        verbose_name_plural = "Perfis Consolidados"
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['shoe_size']),
        ]
    
    def __str__(self):
        return f"Perfil de {self.user.username} ({self.user_type})"
    
    def save(self, *args, **kwargs):
        if self.pk:
            current_profile = UserProfile.objects.get(pk=self.pk)
            self.historical_data.append({
                'timestamp': timezone.now().isoformat(),
                'data': model_to_dict(current_profile)
            })
        super().save(*args, **kwargs)
