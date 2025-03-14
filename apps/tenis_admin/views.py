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
        context.update({
            'total_models': AIModel.objects.count(),
            'approved_models': AIModel.objects.filter(status='approved').count(),
            'review_models': AIModel.objects.filter(status='review').count(),
            'recent_approvals': AIModel.objects.filter(status='approved').order_by('-created_at')[:5]
        })
        return context

class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = AIModel
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    context_object_name = 'model'
    
    def get_success_url(self):
        return reverse_lazy('tenis_admin:manager_dashboard')
    
    def form_valid(self, form):
        try:
            action = form.cleaned_data.get('action')
            model = self.get_object()
            
            if action == 'approve':
                model.status = 'approved'
                messages.success(self.request, 'Modelo aprovado com sucesso!')
            elif action == 'reject':
                model.status = 'rejected'
                messages.success(self.request, 'Modelo rejeitado!')
            
            model.save()
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
        context['metrics'] = model.metrics or {}
        
        # Adicionar métricas detalhadas e gráficos
        try:
            detailed_metrics = MetricsService.get_detailed_metrics(model.id)
            context['detailed_metrics'] = detailed_metrics
        except Exception as e:
            logger.error(f"Erro ao obter métricas detalhadas: {str(e)}")
            messages.error(self.request, 'Erro ao carregar métricas detalhadas')
        
        return context

class MetricsDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Obter métricas gerais do sistema
            system_metrics = MetricsService.get_system_metrics()
            context['system_metrics'] = system_metrics
            
            # Obter modelos de melhor desempenho
            context['top_models'] = AIModel.objects.filter(
                status='approved'
            ).order_by('-metrics__accuracy')[:5]
            
        except Exception as e:
            logger.error(f"Erro ao carregar dashboard de métricas: {str(e)}")
            messages.error(self.request, 'Erro ao carregar métricas do sistema')
        
        return context