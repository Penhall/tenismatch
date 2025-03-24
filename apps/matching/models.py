# /tenismatch/apps/matching/models.py
from django.db import models
from django.conf import settings
from apps.users.models import User

User = settings.AUTH_USER_MODEL

class SneakerProfile(models.Model):
    """
    Perfil de tênis associado a um usuário.
    Contém informações sobre preferências de calçados.
    """
    STYLE_CHOICES = [
        ('ESP', 'Esportivo'),
        ('CAS', 'Casual'),
        ('VIN', 'Vintage'),
        ('SOC', 'Social'),
        ('FAS', 'Fashion')
    ]
    
    COLOR_CHOICES = [
        ('BLK', 'Preto'),
        ('WHT', 'Branco'),
        ('COL', 'Colorido'),
        ('NEU', 'Neutro')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    style = models.CharField(max_length=3, choices=STYLE_CHOICES)
    color = models.CharField(max_length=3, choices=COLOR_CHOICES)
    price_range = models.IntegerField()
    occasion = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'matching_sneakerprofile'  # Corrigido para o nome real da tabela no banco
    
    def __str__(self):
        return f"{self.user.username} - {self.get_style_display()} {self.brand}"
    
    @property
    def sneaker_data(self):
        """
        Retorna dados do tênis em formato dicionário para uso no recomendador.
        """
        return {
            'tenis_marca': self.brand,
            'tenis_estilo': self.get_style_display(),
            'tenis_cores': self.get_color_display(),
            'tenis_preco': self.price_range,
            'tenis_ocasiao': self.occasion
        }

class Match(models.Model):
    """
    Representa um match entre dois usuários.
    Armazena informações sobre compatibilidade e status.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('liked', 'Curtido'),
        ('rejected', 'Rejeitado'),
        ('blocked', 'Bloqueado')
    ]
    
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_b')
    compatibility_score = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_mutual = models.BooleanField(default=False)
    matched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'matching_match'  # Corrigido para o nome real da tabela no banco
        unique_together = ('user_a', 'user_b')
    
    def __str__(self):
        return f"{self.user_a.username} -> {self.user_b.username} ({self.compatibility_score:.1f}%)"
    
    @property
    def user_sneaker(self):
        """Obtém o perfil de tênis do usuário A."""
        return self.user_a.sneakerprofile
    
    @property
    def other_sneaker(self):
        """Obtém o perfil de tênis do usuário B."""
        return self.user_b.sneakerprofile

class MatchFeedback(models.Model):
    """
    Feedback sobre um match, usado para melhorar recomendações futuras.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[
        (1, 'Muito Ruim'),
        (2, 'Ruim'),
        (3, 'Regular'),
        (4, 'Bom'),
        (5, 'Muito Bom')
    ])
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'matching_matchfeedback'  # Corrigido para o nome real da tabela no banco
        unique_together = ('user', 'match')
    
    @property
    def is_positive(self):
        return self.rating >= 4
    
    def __str__(self):
        return f"Feedback de {self.user} para match {self.match_id}"

class DailyRecommendation(models.Model):
    """
    Recomendações diárias para cada usuário.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_recommendations')
    recommended_profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_to')
    compatibility_score = models.FloatField()
    reasons = models.TextField(blank=True)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'matching_dailyrecommendation'  # Adicionado nome da tabela correspondente
        unique_together = ('user', 'recommended_profile', 'created_at')
    
    def __str__(self):
        return f"Recomendação para {self.user.username}: {self.recommended_profile.username}"
    
    def get_reasons(self):
        """Retorna razões de compatibilidade como lista."""
        if not self.reasons:
            return []
        return [r.strip() for r in self.reasons.split(',')]