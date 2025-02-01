# /tenismatch/apps/tenis_admin/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils import timezone
import pandas as pd
from io import StringIO
import logging

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
    ModelDeploymentService, 
    MetricsService, 
    DatasetService
)
from apps.matching.ml.dataset import DatasetPreparation

logger = logging.getLogger(__name__)

# Resto do código permanece igual...

# Mixins
class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ANALISTA'

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'GERENTE'

###################
# Analyst Views
###################

class AnalystDashboardView(LoginRequiredMixin, AnalystRequiredMixin, ListView):
    model = AIModel
    template_name = 'analyst/dashboard.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Remove datasets com arquivos faltantes
        datasets = Dataset.objects.filter(uploaded_by=self.request.user)
        valid_datasets = []
        for dataset in datasets:
            try:
                if dataset.file and dataset.file.path:
                    valid_datasets.append(dataset)
            except FileNotFoundError:
                dataset.delete()  # opcional: remover dataset do banco
                
        context['datasets'] = valid_datasets
        return context

class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = 'analyst/data_upload.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        
        try:
            success, message = DatasetService.process_dataset(self.object.id)
            if success:
                messages.success(self.request, 'Dataset enviado e processado com sucesso!')
            else:
                messages.error(self.request, f'Erro ao processar o dataset: {message}')
                self.object.delete()
                return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f'Erro ao processar o dataset: {str(e)}')
            self.object.delete()
            return redirect(self.get_success_url())
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = Dataset.objects.filter(
            uploaded_by=self.request.user
        ).order_by('-uploaded_at')
        return context

class GenerateDataView(LoginRequiredMixin, AnalystRequiredMixin, FormView):
    template_name = 'analyst/generate_data.html'
    form_class = GenerateDataForm

    def form_valid(self, form):
        data = DatasetPreparation.generate_training_data(form.cleaned_data['n_samples'])
        df = pd.DataFrame(data)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dataset.csv"'
        df.to_csv(response, index=False)
        
        messages.success(self.request, f'Dataset gerado com {form.cleaned_data["n_samples"]} amostras')
        return response

class ModelTrainingView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    form_class = ModelTrainingForm
    template_name = 'analyst/training.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        response = super().form_valid(form)
        
        try:
            # Obter dados de treinamento do dataset
            training_data = DatasetService.get_training_data(form.cleaned_data['dataset'].id)
            
            # Treinar modelo
            metrics = ModelTrainingService.train_model(self.object.id, training_data)
            
            # Atualizar métricas e status
            self.object.metrics = metrics
            self.object.status = 'review'
            self.object.save()
            
            messages.success(
                self.request, 
                f'Modelo treinado com sucesso! Acurácia: {metrics["accuracy"]:.2%}'
            )
        except Exception as e:
            messages.error(self.request, f'Erro no treinamento: {str(e)}')
            self.object.delete()
            return redirect(self.get_success_url())
            
        return response

class ModelTrainingDetailView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = AIModel
    template_name = 'analyst/training_detail.html'
    context_object_name = 'model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'training_metrics': self.object.metrics,
            'dataset': self.object.dataset,
            'status_history': self.object.get_status_history(),
            'performance_metrics': MetricsService.get_model_performance(self.object.id)
        })
        return context

###################
# Manager Views
###################

class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/dashboard.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(status='review')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_models': AIModel.objects.count(),
            'approved_models': AIModel.objects.filter(status='approved').count(),
            'review_models': AIModel.objects.filter(status='review').count(),
            'recent_approvals': AIModel.objects.filter(
                status='approved'
            ).order_by('-updated_at')[:5]
        })
        return context

class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = AIModel
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    success_url = reverse_lazy('tenis_admin:manager_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['metrics'] = self.object.metrics
        context['performance'] = MetricsService.get_model_performance(self.object.id)
        return context

    def form_valid(self, form):
        action = form.cleaned_data.get('decision')
        notes = form.cleaned_data.get('review_notes')
        
        self.object = form.save(commit=False)
        self.object.status = action
        self.object.reviewed_by = self.request.user
        self.object.review_notes = notes
        self.object.reviewed_at = timezone.now()
        
        if action == 'approved':
            try:
                ModelDeploymentService.deploy_model(self.object.id)
                messages.success(self.request, 'Modelo aprovado e implantado com sucesso!')
            except Exception as e:
                messages.error(self.request, f'Erro na implantação: {str(e)}')
                return self.form_invalid(form)
        else:
            messages.warning(self.request, 'Modelo rejeitado.')
            
        self.object.save()
        return super().form_valid(form)

class MetricsDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = int(self.request.GET.get('period', 30))
        
        metrics_service = MetricsService()
        model_metrics = metrics_service.get_model_performance_metrics(days=period)
        daily_metrics = metrics_service.get_daily_model_metrics(days=period)
        
        context.update({
            'model_metrics': model_metrics,
            'daily_metrics': {
                'dates': [m['date'].strftime('%d/%m') for m in daily_metrics],
                'accuracies': [m['avg_accuracy'] for m in daily_metrics],
                'precisions': [m['avg_precision'] for m in daily_metrics],
                'recalls': [m['avg_recall'] for m in daily_metrics],
                'f1_scores': [m['avg_f1_score'] for m in daily_metrics]
            },
            'total_models': AIModel.objects.count(),
            'models_in_review': AIModel.objects.filter(status='review').count(),
            'approved_models': AIModel.objects.filter(status='approved').count()
        })
        
        return context

class ModelPerformanceView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = AIModel
    template_name = 'manager/model_performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'metrics': self.object.metrics,
            'performance': MetricsService.get_model_performance(self.object.id),
            'history': self.object.get_status_history(),
            'recent_matches': MetricsService.get_recent_matches(self.object.id)
        })
        return context
        

################### DATASET PREVIEW AND MAPPING VIEWS ###################

class DatasetPreviewView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = Dataset
    template_name = 'analyst/mapping/preview.html'
    context_object_name = 'dataset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            preview = DatasetService.get_preview_data(self.object.id)
            context['preview'] = preview
        except Exception as e:
            messages.error(self.request, f'Erro ao carregar preview: {str(e)}')
            context['preview'] = {'columns': [], 'data': [], 'total_rows': 0}
        return context

class DatasetMappingView(LoginRequiredMixin, AnalystRequiredMixin, FormView):
    template_name = 'analyst/mapping/mapping.html'
    form_class = DatasetMappingForm

    def dispatch(self, request, *args, **kwargs):
        self.dataset = get_object_or_404(Dataset, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['columns'] = DatasetService.get_dataset_columns(self.dataset.id)
        return kwargs

    def form_valid(self, form):
        mapping = {
            field.replace('mapping_', ''): value 
            for field, value in form.cleaned_data.items() 
            if field.startswith('mapping_')
        }
        
        # Validar e salvar mapeamento
        success, message = DatasetService.validate_mapping(self.dataset.id, mapping)
        if not success:
            messages.error(self.request, message)
            return self.form_invalid(form)
            
        # Criar/atualizar mapeamento
        column_mapping, _ = ColumnMapping.objects.get_or_create(dataset=self.dataset)
        column_mapping.mapping = mapping
        column_mapping.is_validated = True
        column_mapping.save()
        
        # Processar dataset
        success, message = DatasetService.process_dataset(self.dataset.id)
        if not success:
            messages.error(self.request, message)
            return self.form_invalid(form)
            
        messages.success(self.request, 'Dataset mapeado e processado com sucesso!')
        return redirect('tenis_admin:analyst_dashboard')
