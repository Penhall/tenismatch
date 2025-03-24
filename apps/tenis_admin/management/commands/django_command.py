# /tenismatch/apps/tenis_admin/management/commands/update_metrics.py
"""
Comando Django para atualizar métricas dos modelos.
Uso: python manage.py update_metrics
"""
from django.core.management.base import BaseCommand
from apps.tenis_admin.models import AIModel
from apps.tenis_admin.services.metrics_service import MetricsService
import random

class Command(BaseCommand):
    help = 'Atualiza as métricas dos modelos de IA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate',
            action='store_true',
            help='Gerar métricas aleatórias para modelos sem métricas',
        )
        
    def handle(self, *args, **options):
        # Atualizar métricas existentes
        self.stdout.write(self.style.WARNING('Atualizando métricas dos modelos...'))
        updated_count = MetricsService.update_all_models_metrics()
        self.stdout.write(self.style.SUCCESS(f'{updated_count} modelos foram atualizados'))

        # Gerar métricas aleatórias se solicitado
        if options['generate']:
            self.stdout.write(self.style.WARNING('Gerando métricas aleatórias para modelos sem métricas...'))
            models_without_metrics = AIModel.objects.filter(metrics__isnull=True) | AIModel.objects.filter(metrics={})
            
            for model in models_without_metrics:
                # Gerar métricas aleatórias para teste
                metrics = {
                    'accuracy': round(random.uniform(75, 95), 2),
                    'precision': round(random.uniform(70, 90), 2),
                    'recall': round(random.uniform(60, 95), 2),
                    'f1_score': round(random.uniform(65, 90), 2)
                }
                
                model.metrics = metrics
                model.save()
                self.stdout.write(f'Geradas métricas para o modelo {model.id} ({model.name})')
                
            self.stdout.write(
                self.style.SUCCESS(f'Métricas geradas para {models_without_metrics.count()} modelos')
            )