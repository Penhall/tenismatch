# /tenismatch/apps/tenis_admin/models.py 
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Dataset(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='datasets/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    records_count = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    stats = models.JSONField(null=True, blank=True)  # Estatísticas do dataset

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Rascunho'),
        ('review', 'Em Revisão'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado')
    ])
    metrics = models.JSONField(null=True, blank=True)  # Métricas do modelo
    model_file = models.FileField(upload_to='models/', null=True)