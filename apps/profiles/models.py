# /tenismatch/apps/profiles/models.py 
from django.db import models
from apps.users.models import User

class Profile(models.Model):
    BRAND_CHOICES = [
        ('Nike', 'Nike'),
        ('Adidas', 'Adidas'),
        ('Puma', 'Puma'),
        ('Asics', 'Asics'),
    ]
    
    STYLE_CHOICES = [
        ('Corrida', 'Corrida'),
        ('Casual', 'Casual'),
        ('Tênis', 'Tênis'),
        ('Basquete', 'Basquete'),
    ]
    
    COLOR_CHOICES = [
        ('Branco', 'Branco'),
        ('Azul', 'Azul'),
        ('Preto', 'Preto'),
        ('Vermelho', 'Vermelho'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    age_min = models.IntegerField(default=18)
    age_max = models.IntegerField(default=50)
    location_preference = models.CharField(max_length=100, blank=True)
    preferred_brands = models.CharField(max_length=100, choices=BRAND_CHOICES, blank=True)
    preferred_styles = models.CharField(max_length=100, choices=STYLE_CHOICES, blank=True)
    preferred_colors = models.CharField(max_length=100, choices=COLOR_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def calculate_tennis_compatibility(self, tennis_profile):
        """Calcula a compatibilidade com base nas preferências de tênis"""
        score = 0
        
        if self.preferred_brands and tennis_profile['tenis_marca'] == self.preferred_brands:
            score += 1
            
        if self.preferred_styles and tennis_profile['tenis_estilo'] == self.preferred_styles:
            score += 1
            
        if self.preferred_colors and tennis_profile['tenis_cores'] == self.preferred_colors:
            score += 1
            
        return score / 3  # Retorna um valor entre 0 e 1
