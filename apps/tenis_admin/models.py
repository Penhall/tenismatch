# /tenismatch/apps/tenis_admin/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Dataset(models.Model):
    DATASET_TYPES = [
        ('upload', 'Upload'),
        ('generated', 'Gerado')
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processando'),
        ('mapping', 'Aguardando Mapeamento'),
        ('ready', 'Pronto')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='datasets/')
    records_count = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    dataset_type = models.CharField(max_length=20, choices=DATASET_TYPES, default='upload')
    file_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    stats = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return self.name

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Rascunho'),
        ('review', 'Em Revisão'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado')
    ])
    metrics = models.JSONField(null=True, blank=True)

class ColumnMapping(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='column_mapping')
    mapping = models.JSONField(default=dict)
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Mapeamento para {self.dataset.name}"