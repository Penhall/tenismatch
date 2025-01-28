# /tenismatch/apps/matching/models.py 
from django.db import models
from apps.users.models import User
from django.conf import settings

class SneakerProfile(models.Model):
    STYLE_CHOICES = [
        ('ESP', 'Esportivo'),
        ('CAS', 'Casual'),
        ('VIN', 'Vintage'),
        ('SOC', 'Social'),
        ('FAS', 'Fashion'),
    ]

    COLOR_CHOICES = [
        ('BLK', 'Preto'),
        ('WHT', 'Branco'),
        ('COL', 'Colorido'),
        ('NEU', 'Neutro'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    style = models.CharField(max_length=3, choices=STYLE_CHOICES)
    color = models.CharField(max_length=3, choices=COLOR_CHOICES)
    price_range = models.IntegerField()
    occasion = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sneaker_profiles'

class Match(models.Model):
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_b')
    compatibility_score = models.FloatField()
    matched_at = models.DateTimeField(auto_now_add=True)
    is_mutual = models.BooleanField(default=False)

    class Meta:
        db_table = 'matches'
        unique_together = ('user_a', 'user_b')
        
class MatchFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
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
        unique_together = ('user', 'match')
        
    @property
    def is_positive(self):
        return self.rating >= 4
        
    def __str__(self):
        return f"Feedback de {self.user} para match {self.match_id}"