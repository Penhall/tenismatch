# /tenismatch/apps/tenis_admin/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import pandas as pd
from io import StringIO
import logging
import os
import time
import threading
from django.core.files.base import ContentFile
from .services.dataset_service import DatasetService
from .services.metrics_service import MetricsService

from .models import AIModel, Dataset, ColumnMapping
from .forms import (
    DatasetUploadForm,
    ModelTrainingForm,
    ModelReviewForm,
    GenerateDataForm,
    DatasetMappingForm
)
from .services import (
    ModelTrainingService,
    ModelDeploymentService
)
from apps.matching.ml.dataset import DatasetPreparation

logger = logging.getLogger(__name__)

# Mixins
class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ANALISTA'

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'GERENTE'

# Dashboard Views
class AnalystDashboardView(LoginRequiredMixin, AnalystRequiredMixin, TemplateView):
    template_name = 'analyst/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Forçar sincronização de datasets ao carregar o dashboard
            DatasetService.sync_datasets()
            
            # Buscar todos os datasets
            datasets = Dataset.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
            
            # Buscar todos os modelos
            models = AIModel.objects.filter(created_by=self.request.user).order_by('-created_at')
            
            # Adicionar ao contexto
            context['datasets'] = datasets
            context['models'] = models
            
            # Estatísticas para o dashboard
            context.update({
                'total_datasets': datasets.count(),
                'ready_datasets': datasets.filter(status='ready').count(),
                'mapping_datasets': datasets.filter(status='mapping').count(),
                'total_models': models.count(),
                'review_models': models.filter(status='review').count(),
                'approved_models': models.filter(status='approved').count()
            })
            
            # Debug info
            logger.info(f"Usuário: {self.request.user.username}, Datasets: {datasets.count()}, Modelos: {models.count()}")
            for dataset in datasets:
                logger.info(f"Dataset: {dataset.id}, {dataset.name}, Status: {dataset.status}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dashboard: {str(e)}")
            messages.error(self.request, f"Erro ao carregar dados: {str(e)}")
        
        return context

class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = 'analyst/data_upload.html'  # Note: usando data_upload.html em vez de dataset_upload.html
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Dataset carregado com sucesso!')
        return super().form_valid(form)

# Dataset Preview View
class DatasetPreviewView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = Dataset
    template_name = 'analyst/dataset_preview.html'
    context_object_name = 'dataset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            dataset = self.get_object()
            df = pd.read_csv(dataset.file.path)
            context['preview_data'] = df.head(10).to_html(classes='table table-striped', index=False)
        except Exception as e:
            logger.error(f"Erro ao visualizar dataset: {str(e)}")
            messages.error(self.request, f'Erro ao carregar dataset: {str(e)}')
        return context

# Dataset Mapping View
class DatasetMappingView(LoginRequiredMixin, AnalystRequiredMixin, UpdateView):
    model = Dataset
    form_class = DatasetMappingForm
    template_name = 'analyst/dataset_mapping.html'
    context_object_name = 'dataset'
    
    def get_success_url(self):
        return reverse_lazy('tenis_admin:analyst_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            dataset = self.get_object()
            df = pd.read_csv(dataset.file.path)
            context['columns'] = df.columns.tolist()
            context['preview_data'] = df.head(5).to_html(classes='table table-striped', index=False)
        except Exception as e:
            logger.error(f"Erro ao carregar colunas do dataset: {str(e)}")
            messages.error(self.request, f'Erro ao carregar dataset: {str(e)}')
        return context
    
    def form_valid(self, form):
        try:
            # Salvar o mapeamento de colunas
            mapping_data = form.cleaned_data.get('column_mapping', {})
            dataset = self.get_object()
            
            # Criar ou atualizar o objeto ColumnMapping
            column_mapping, created = ColumnMapping.objects.get_or_create(
                dataset=dataset,
                defaults={'mapping': mapping_data}
            )
            
            if not created:
                column_mapping.mapping = mapping_data
                column_mapping.save()
            
            # Atualizar status do dataset
            dataset.status = 'ready'
            dataset.save()
            
            messages.success(self.request, 'Mapeamento de colunas salvo com sucesso!')
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Erro ao salvar mapeamento: {str(e)}")
            messages.error(self.request, f'Erro ao salvar mapeamento: {str(e)}')
            return self.form_invalid(form)

class GenerateDataView(LoginRequiredMixin, AnalystRequiredMixin, FormView):
    template_name = 'analyst/generate_data.html'
    form_class = GenerateDataForm
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        try:
            synthetic_data = form.generate_synthetic_data()
            dataset = Dataset.objects.create(
                name=f"Synthetic Dataset {timezone.now().strftime('%Y%m%d%H%M%S')}",
                file=ContentFile(
                    synthetic_data.to_csv(index=False),
                    name=f"synthetic_{timezone.now().strftime('%Y%m%d%H%M%S')}.csv"
                ),
                description="Dataset gerado automaticamente",
                uploaded_by=self.request.user,
                file_type='csv'
            )
            messages.success(self.request, 'Dataset sintético gerado com sucesso!')
            return redirect(self.get_success_url())
        except Exception as e:
            logger.error(f"Erro na geração de dados: {str(e)}", exc_info=True)
            messages.error(self.request, f'Erro ao gerar dados: {str(e)}')
            return self.form_invalid(form)

class ModelTrainingView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    form_class = ModelTrainingForm
    template_name = 'analyst/model_training.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.status = 'draft'
            response = super().form_valid(form)
            
            # Iniciar treinamento do modelo
            success, message = ModelTrainingService.train_model(
                self.object.id, 
                form.cleaned_data.get('dataset').id
            )
            
            if success:
                messages.success(self.request, 'Modelo criado e treinado com sucesso!')
                self.object.status = 'review'
                self.object.save()
            else:
                messages.error(self.request, f'Erro no treinamento: {message}')
                
            return response
        except Exception as e:
            logger.error(f"Erro no treinamento do modelo: {str(e)}")
            messages.error(self.request, 'Erro no treinamento do modelo')
            return self.form_invalid(form)

class ModelTrainingDetailView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = AIModel
    template_name = 'analyst/model_detail.html'
    context_object_name = 'model'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_object()
        context['metrics'] = model.metrics or {}
        return context

def model_training_progress(request, model_id):
    try:
        model = get_object_or_404(AIModel, id=model_id)
        # Simulação de progresso de treinamento
        progress = {
            'status': model.status,
            'progress': 100 if model.status in ['review', 'approved'] else 50,
            'message': 'Treinamento concluído' if model.status in ['review', 'approved'] else 'Treinamento em andamento'
        }
        return JsonResponse(progress)
    except Exception as e:
        logger.error(f"Erro ao obter progresso: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

# Manager Views
class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/dashboard.html'
    context_object_name = 'models'
    
    def get_queryset(self):
        return AIModel.objects.filter(status='review').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas básicas
        context['total_models'] = AIModel.objects.count()
        context['in_review'] = AIModel.objects.filter(status='review').count()
        context['approved_models'] = AIModel.objects.filter(status='approved').count()
        context['rejected_models'] = AIModel.objects.filter(status='rejected').count()
        
        # Métricas médias dos modelos - utilizando a função do MetricsService
        metrics = MetricsService.calculate_average_metrics()
        context['avg_metrics'] = metrics
        
        # Modelos recentes para links no sidebar
        context['latest_model_for_review'] = AIModel.objects.filter(status='review').order_by('-created_at').first()
        context['latest_approved_model'] = AIModel.objects.filter(status='approved').order_by('-created_at').first()
        context['models_in_review'] = AIModel.objects.filter(status='review').count()
        
        return context

# /tenismatch/apps/tenis_admin/views.py (apenas a classe ModelReviewView)

class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, FormView):
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    
    def get_success_url(self):
        return reverse_lazy('tenis_admin:manager_dashboard')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Remover a passagem de 'instance' para o form
        return kwargs
    
    def get_object(self):
        # Método auxiliar para manter a compatibilidade com o código existente
        return get_object_or_404(AIModel, pk=self.kwargs.get('pk'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_object()
        
        # Adicionar o modelo ao contexto, já que não está mais sendo feito automaticamente
        context['model'] = model
        
        # Adiciona métricas
        context['metrics'] = model.metrics or {}
        
        # Adiciona models recentes para sidebar
        context['latest_model_for_review'] = AIModel.objects.filter(status='review').order_by('-created_at').first()
        context['latest_approved_model'] = AIModel.objects.filter(status='approved').order_by('-created_at').first()
        context['models_in_review'] = AIModel.objects.filter(status='review').count()
        
        return context
    
    def form_valid(self, form):
        try:
            # Correto para casar com o nome do campo no form
            decision = form.cleaned_data.get('decision')
            model = self.get_object()
            
            if decision == 'approve':
                # Usar o serviço para garantir o processamento correto
                success, message = ModelTrainingService.review_model(model.id, True, form.cleaned_data.get('review_notes'))
                if success:
                    messages.success(self.request, 'Modelo aprovado com sucesso!')
                else:
                    messages.error(self.request, f'Erro na aprovação: {message}')
                    return self.form_invalid(form)
            elif decision == 'reject':
                success, message = ModelTrainingService.review_model(model.id, False, form.cleaned_data.get('review_notes'))
                if success:
                    messages.success(self.request, 'Modelo rejeitado!')
                else:
                    messages.error(self.request, f'Erro na rejeição: {message}')
                    return self.form_invalid(form)
            
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Erro na revisão do modelo: {str(e)}")
            messages.error(self.request, f'Erro na revisão: {str(e)}')
            return self.form_invalid(form)

class ModelPerformanceView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = AIModel
    template_name = 'manager/model_performance.html'
    context_object_name = 'model'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_object()
        
        # Adiciona métricas
        context['metrics'] = model.metrics or {}
        
        # Adiciona models recentes para sidebar
        context['latest_model_for_review'] = AIModel.objects.filter(status='review').order_by('-created_at').first()
        context['latest_approved_model'] = AIModel.objects.filter(status='approved').order_by('-created_at').first()
        context['models_in_review'] = AIModel.objects.filter(status='review').count()
        
        return context

class MetricsDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Obter resumo de métricas
            metrics_summary = MetricsService.get_metrics_summary()
            context.update(metrics_summary)
            
            # Adicionar modelos recentes para links no sidebar
            context['latest_model_for_review'] = AIModel.objects.filter(status='review').order_by('-created_at').first()
            context['latest_approved_model'] = AIModel.objects.filter(status='approved').order_by('-created_at').first()
            context['models_in_review'] = AIModel.objects.filter(status='review').count()
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {str(e)}")
            messages.error(self.request, f"Erro ao carregar métricas: {str(e)}")
            
            # Fornecer dados vazios para evitar erros no template
            context.update({
                'total_models': 0,
                'approved_models': 0,
                'rejected_models': 0,
                'in_review': 0,
                'approval_rate': 0,
                'model_metrics': {
                    'avg_accuracy': 0,
                    'avg_precision': 0,
                    'avg_recall': 0,
                    'avg_f1_score': 0
                },
                'daily_model_metrics': {
                    'dates': [],
                    'accuracies': [],
                    'precisions': [],
                    'recalls': [],
                    'f1_scores': []
                }
            })
        
        return context

# Adicionando a view de Approvals que faltava
class ApprovalsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/approvals.html'
    context_object_name = 'pending_models'
    
    def get_queryset(self):
        return AIModel.objects.filter(status='review').order_by('-created_at')

# Funções auxiliares para aprovação/rejeição de modelos
def approve_model(request, model_id):
    model = get_object_or_404(AIModel, id=model_id)
    if request.method == 'POST':
        review_notes = request.POST.get('review_notes', '')
        model.status = 'approved'
        model.save()
        messages.success(request, f'Modelo {model.name} aprovado com sucesso!')
    return redirect('tenis_admin:manager_dashboard')

def reject_model(request, model_id):
    model = get_object_or_404(AIModel, id=model_id)
    if request.method == 'POST':
        review_notes = request.POST.get('review_notes', '')
        model.status = 'rejected'
        model.save()
        messages.success(request, f'Modelo {model.name} rejeitado.')
    return redirect('tenis_admin:manager_dashboard')