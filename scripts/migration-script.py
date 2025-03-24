# /tenismatch/scripts/update_metrics.py
"""
Script para atualizar as métricas dos modelos existentes para garantir
que todos estejam no formato de porcentagem (0-100).
"""
import os
import sys
import django
from django.db.models import F, Q

# Configure Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.tenis_admin.models import AIModel
from apps.tenis_admin.services.metrics_service import MetricsService
import random
import logging

logger = logging.getLogger(__name__)

def update_existing_metrics():
    """Atualiza as métricas dos modelos existentes para o formato de porcentagem."""
    models = AIModel.objects.all()
    updated_count = 0
    missing_metrics_count = 0
    
    for model in models:
        if model.metrics:
            # Verificar se as métricas já estão no formato correto
            metrics_updated = False
            for key in ['accuracy', 'precision', 'recall', 'f1_score']:
                if key in model.metrics and model.metrics[key] is not None:
                    # Se o valor for menor que 1, é uma proporção e deve ser convertida para porcentagem
                    if model.metrics[key] <= 1:
                        model.metrics[key] = model.metrics[key] * 100
                        metrics_updated = True
            
            if metrics_updated:
                model.save()
                updated_count += 1
                print(f"Atualizado modelo {model.id} ({model.name})")
        else:
            missing_metrics_count += 1
    
    print(f"\nResultado:")
    print(f"- {updated_count} modelos tiveram suas métricas atualizadas")
    print(f"- {missing_metrics_count} modelos não possuem métricas")
    return updated_count, missing_metrics_count

def generate_random_metrics():
    """Gera métricas aleatórias para modelos que não possuem métricas."""
    models_without_metrics = AIModel.objects.filter(
        Q(metrics__isnull=True) | Q(metrics={})
    )
    updated_count = 0
    
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
        updated_count += 1
        print(f"Geradas métricas para o modelo {model.id} ({model.name})")
    
    print(f"\nResultado:")
    print(f"- {updated_count} modelos receberam métricas aleatórias")
    return updated_count

if __name__ == "__main__":
    print("======= ATUALIZADOR DE MÉTRICAS =======")
    print("Este script atualiza as métricas de todos os modelos existentes.")
    choice = input("\nDeseja: \n1. Atualizar formato das métricas existentes\n2. Gerar métricas aleatórias para modelos sem métricas\n3. Ambos\nEscolha (1/2/3): ")
    
    if choice == '1' or choice == '3':
        updated, missing = update_existing_metrics()
        
    if choice == '2' or choice == '3':
        generated = generate_random_metrics()
    
    print("\nOperação concluída com sucesso.")