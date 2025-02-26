from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
import pandas as pd
from io import StringIO
import logging
import os
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
        
        # Obter todos os datasets do usuário
        datasets = Dataset.objects.filter(uploaded_by=self.request.user)
        
        # Verificar quais datasets têm arquivos válidos
        valid_datasets = []
        invalid_datasets = []
        
        for dataset in datasets:
            try:
                if dataset.file and os.path.exists(dataset.file.path):
                    valid_datasets.append(dataset)
                else:
                    invalid_datasets.append(dataset)
                    logger.warning(f"Dataset {dataset.id} ({dataset.name}) tem arquivo inválido ou inexistente: {dataset.file}")
            except Exception as e:
                invalid_datasets.append(dataset)
                logger.error(f"Erro ao verificar arquivo do dataset {dataset.id} ({dataset.name}): {str(e)}")
        
        # Registrar quantos datasets foram considerados inválidos
        if invalid_datasets:
            logger.warning(f"{len(invalid_datasets)} datasets com arquivos inválidos foram encontrados")
        
        context['datasets'] = valid_datasets
        context['invalid_datasets_count'] = len(invalid_datasets)
        
        # Adiciona contagens de modelos por status
        context['models_in_review'] = AIModel.objects.filter(created_by=self.request.user, status='review').count()
        context['approved_models'] = AIModel.objects.filter(created_by=self.request.user, status='approved').count()
        context['rejected_models'] = AIModel.objects.filter(created_by=self.request.user, status='rejected').count()
        context['total_models'] = AIModel.objects.filter(created_by=self.request.user).count()
        
        return context

class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = 'analyst/data_upload.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        # Salva o nome do dataset antes de processar o arquivo
        dataset_name = form.cleaned_data.get('name')
        form.instance.uploaded_by = self.request.user
        form.instance.name = dataset_name
        form.instance.status = 'ready'  # Inicia como ready para testes
        
        response = super().form_valid(form)
        
        try:
            # Renomeia o arquivo para o nome escolhido pelo analista
            original_path = self.object.file.path
            original_name, original_ext = os.path.splitext(os.path.basename(original_path))
            new_filename = f"{dataset_name}{original_ext}"
            new_path = os.path.join(os.path.dirname(original_path), new_filename)
            
            os.rename(original_path, new_path)
            self.object.file.name = os.path.join(os.path.dirname(self.object.file.name), new_filename)
            
            # Atualiza o status e salva
            self.object.status = 'ready'
            self.object.save()
            
            # Verifica se o arquivo foi salvo corretamente
            if not self.object.file or not os.path.exists(new_path):
                raise FileNotFoundError('Arquivo não encontrado após upload')
                
            messages.success(self.request, 'Dataset enviado com sucesso!')
                
        except Exception as e:
            logger.error(f'Erro no upload do dataset: {str(e)}')
            messages.error(self.request, f'Erro ao validar o dataset: {str(e)}')
            self.object.delete()
            return redirect(self.get_success_url())
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_datasets = DatasetService.sync_datasets(self.request.user)
        if new_datasets > 0:
            messages.info(self.request, f'{new_datasets} novos datasets encontrados.')
        context['datasets'] = Dataset.objects.filter(
            uploaded_by=self.request.user
        ).order_by('-uploaded_at')
        return context

class GenerateDataView(LoginRequiredMixin, AnalystRequiredMixin, FormView):
    form_class = GenerateDataForm
    template_name = 'analyst/generate_data.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        n_samples = form.cleaned_data.get('n_samples')
        include_labels = form.cleaned_data.get('include_labels')
        
        try:
            # Implementar lógica para gerar dados sintéticos
            generated_data = self.generate_synthetic_data(n_samples, include_labels)
            
            # Salvar o dataset gerado
            dataset = Dataset.objects.create(
                name=f"synthetic_dataset_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                description="Dataset sintético gerado automaticamente.",
                uploaded_by=self.request.user,
                file_size=len(generated_data),  # Ajustado para refletir tamanho correto
                file_type='csv',
                is_processed=True
            )
            
            # Salvar o arquivo gerado
            dataset.file.save(f"{dataset.name}.csv", ContentFile(generated_data))
            
            messages.success(self.request, 'Dataset sintético gerado e salvo com sucesso!')
        except Exception as e:
            logger.error(f'Erro ao gerar dataset sintético: {str(e)}')
            messages.error(self.request, f'Erro ao gerar dataset sintético: {str(e)}')
            return redirect(self.get_success_url())
        
        return super().form_valid(form)

    def generate_synthetic_data(self, n_samples, include_labels):
        # Simulação de geração de dados
        data = {
            'tenis_marca': [f"Marca_{i}" for i in range(n_samples)],
            'tenis_estilo': [f"Estilo_{i%5}" for i in range(n_samples)],
            'tenis_cores': [f"Cor_{i%3}" for i in range(n_samples)],
            'tenis_preco': [round(50 + i * 1.5, 2) for i in range(n_samples)]
        }
        if include_labels:
            data['label'] = [1 if i % 2 == 0 else 0 for i in range(n_samples)]
        
        df = pd.DataFrame(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_file = csv_buffer.getvalue().encode('utf-8')
        return csv_file

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DatasetPreviewView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = Dataset
    template_name = 'analyst/dataset_preview.html'
    context_object_name = 'dataset'

class DatasetMappingView(LoginRequiredMixin, AnalystRequiredMixin, UpdateView):
    model = ColumnMapping
    form_class = DatasetMappingForm
    template_name = 'analyst/dataset_mapping.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def get_object(self, queryset=None):
        dataset = get_object_or_404(Dataset, pk=self.kwargs['pk'])
        mapping, created = ColumnMapping.objects.get_or_create(dataset=dataset)
        return mapping

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        dataset = get_object_or_404(Dataset, pk=self.kwargs['pk'])
        df = pd.read_csv(dataset.file.path)
        kwargs['columns'] = df.columns.tolist()
        return kwargs

class ModelTrainingView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    form_class = ModelTrainingForm
    template_name = 'analyst/model_creation.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Sincroniza datasets antes de exibir o form
        try:
            new_datasets = DatasetService.sync_datasets(self.request.user)
            if new_datasets > 0:
                messages.info(self.request, f'{new_datasets} novos datasets encontrados.')
        except Exception as e:
            logger.error(f"Erro ao sincronizar datasets: {str(e)}")
            messages.warning(self.request, f"Erro ao sincronizar datasets: {str(e)}")
        
        # Atualiza queryset do campo dataset
        try:
            datasets = Dataset.objects.filter(status='ready')
            # Verificar quais datasets têm arquivos válidos
            valid_datasets_ids = []
            for dataset in datasets:
                try:
                    if dataset.file and os.path.exists(dataset.file.path):
                        valid_datasets_ids.append(dataset.id)
                except Exception as e:
                    logger.error(f"Erro ao verificar arquivo do dataset {dataset.id}: {str(e)}")
            
            # Filtrar apenas datasets válidos
            form.fields['dataset'].queryset = Dataset.objects.filter(id__in=valid_datasets_ids).order_by('-uploaded_at')
            
            # Verificar se há datasets disponíveis
            if not form.fields['dataset'].queryset.exists():
                messages.warning(self.request, 'Não há datasets válidos disponíveis para treinamento. Por favor, faça upload de um dataset primeiro.')
        except Exception as e:
            logger.error(f"Erro ao atualizar queryset de datasets: {str(e)}")
            messages.error(self.request, f"Erro ao carregar datasets: {str(e)}")
        
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'  # Iniciar como rascunho
        
        # Verificar se o dataset existe e é válido
        dataset = form.cleaned_data.get('dataset')
        if not dataset or not dataset.file or not os.path.exists(dataset.file.path):
            messages.error(self.request, 'O dataset selecionado não é válido ou não existe.')
            return self.form_invalid(form)
        
        # Salvar o modelo
        response = super().form_valid(form)
        
        try:
            # Processa o modelo somente após a criação do dataset
            logger.info(f"Iniciando treinamento do modelo {self.object.id} com o dataset {dataset.id}")
            success, message = ModelTrainingService.train_model(self.object.id, dataset.id)
            
            if success:
                messages.success(self.request, 'Modelo treinado com sucesso e enviado para revisão!')
                logger.info(f"Modelo {self.object.id} treinado com sucesso")
            else:
                logger.error(f"Falha ao treinar modelo {self.object.id}: {message}")
                messages.error(self.request, f'Erro ao treinar o modelo: {message}')
                # Não excluir o modelo, apenas marcar como falha
                self.object.status = 'rejected'
                self.object.save()
        except Exception as e:
            logger.error(f'Erro no treinamento do modelo {self.object.id}: {str(e)}')
            messages.error(self.request, f'Erro ao treinar o modelo: {str(e)}')
            # Não excluir o modelo, apenas marcar como falha
            self.object.status = 'rejected'
            self.object.save()
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['models'] = AIModel.objects.filter(
            created_by=self.request.user
        ).order_by('-created_at')
        
        # Adicionar informações sobre datasets disponíveis
        datasets = Dataset.objects.filter(uploaded_by=self.request.user)
        valid_datasets = []
        for dataset in datasets:
            try:
                if dataset.file and os.path.exists(dataset.file.path):
                    valid_datasets.append(dataset)
            except Exception as e:
                logger.error(f"Erro ao verificar arquivo do dataset {dataset.id}: {str(e)}")
        
        context['available_datasets'] = valid_datasets
        context['datasets_count'] = len(valid_datasets)
        
        return context

class ModelTrainingDetailView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = AIModel
    template_name = 'analyst/model_detail.html'
    context_object_name = 'model'

class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metrics_summary = MetricsService.get_metrics_summary()
        context.update(metrics_summary)
        return context

class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, FormView):
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    success_url = reverse_lazy('tenis_admin:manager_dashboard')

    def form_valid(self, form):
        model_id = self.kwargs['pk']
        decision = form.cleaned_data.get('decision')
        review_notes = form.cleaned_data.get('review_notes')
        
        model = get_object_or_404(AIModel, pk=model_id)
        
        try:
            if decision == 'approved':
                model.status = 'approved'
            elif decision == 'rejected':
                model.status = 'rejected'
            model.save()
            messages.success(self.request, f'Modelo {decision} com sucesso!')
        except Exception as e:
            logger.error(f'Erro ao revisar o modelo: {str(e)}')
            messages.error(self.request, f'Erro ao revisar o modelo: {str(e)}')
            return redirect(self.get_success_url())
        
        return super().form_valid(form)

class ModelPerformanceView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = AIModel
    template_name = 'manager/model_performance.html'
    context_object_name = 'model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_metrics = MetricsService.get_model_metrics(self.object.id)
        if model_metrics:
            context['metrics'] = model_metrics
        return context

class MetricsDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/metrics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter métricas médias
        model_metrics = MetricsService.calculate_average_metrics()
        context['model_metrics'] = model_metrics
        
        # Obter métricas diárias
        daily_metrics = MetricsService.get_daily_metrics()
        context['daily_model_metrics'] = daily_metrics
        
        # Adicionar métricas gerais
        metrics_summary = MetricsService.get_metrics_summary()
        context.update(metrics_summary)
        
        return context
