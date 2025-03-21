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
    file_type = models.CharField(
        max_length=10,
        choices=[("csv", "CSV"), ("json", "JSON"), ("xlsx", "Excel")],
        default="csv",
    )
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Rascunho'),
        ('review', 'Em Revisão'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado')
    ])
    metrics = models.JSONField(null=True, blank=True)
    # Adicionar o campo model_file que está faltando
    model_file = models.FileField(upload_to='models/', null=True, blank=True)
    
    # Campos para rastreamento de progresso
    TRAINING_STATUS_CHOICES = [
        ('queued', 'Na Fila'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou')
    ]
    
    training_status = models.CharField(
        max_length=20, 
        choices=TRAINING_STATUS_CHOICES,
        default='queued'
    )
    training_progress = models.FloatField(default=0)  # 0-100
    training_message = models.CharField(max_length=255, blank=True, null=True)
    training_started_at = models.DateTimeField(null=True, blank=True)
    training_completed_at = models.DateTimeField(null=True, blank=True)

    # Campos para revisão
    review_notes = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_models'
    )

    def __str__(self):
        return f"{self.name} v{self.version}"

    def get_status_display(self):
        return dict(self._meta.get_field('status').choices)[self.status]

    def get_training_status_display(self):
        return dict(self.TRAINING_STATUS_CHOICES)[self.training_status]

class ColumnMapping(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='column_mapping')
    mapping = models.JSONField(default=dict)
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    required_columns = {
        'tenis_marca': 'Marca',
        'tenis_estilo': 'Estilo',
        'tenis_cores': 'Cores',
        'tenis_preco': 'Preço'
    }

    def __str__(self):
        return f"Mapeamento para {self.dataset.name}"
    
    def get_missing_mappings(self):
        """
        Retorna uma lista de colunas requeridas que ainda não foram mapeadas.
        
        Returns:
            list: Lista de nomes de colunas que ainda precisam ser mapeadas
        """
        mapped_columns = set(self.mapping.values())
        required_columns = set(self.required_columns.keys())
        return list(required_columns - mapped_columns)