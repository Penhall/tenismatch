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
import json
from django.core.files.base import ContentFile
from .services.dataset_service import DatasetService
from .services.metrics_service import MetricsService

from .utils import TimingUtil

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
        return True  # Permitir acesso a qualquer usuário temporariamente
        
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
class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        logger.info(f"Iniciando GET ManagerDashboard para usuário: {request.user.username}")
        start_time = time.time()
        response = super().get(request, *args, **kwargs)
        total_time = time.time() - start_time
        logger.info(f"Tempo total ManagerDashboard.get: {total_time:.4f}s")
        return response
    
    def get_context_data(self, **kwargs):
        logger.info("Iniciando ManagerDashboardView.get_context_data")
        start_time = time.time()
        
        # Log tempo antes de chamar o parent
        parent_start = time.time()
        context = super().get_context_data(**kwargs)
        parent_time = time.time() - parent_start
        logger.info(f"Tempo parent get_context_data: {parent_time:.4f}s")
        
        # Estatísticas - mantendo contagens existentes
        counts_start = time.time()
        try:
            total_count = AIModel.objects.count()
            approved_count = AIModel.objects.filter(status='approved').count()
            review_count = AIModel.objects.filter(status='review').count()
            rejected_count = AIModel.objects.filter(status='rejected').count()
            
            context.update({
                'total_models': total_count,
                'approved_models_count': approved_count,  # Original
                'approved_models': approved_count,        # Nova convenção
                'review_models_count': review_count,      # Original
                'review_models': review_count,            # Nova convenção
                'in_review': review_count,                # Compatibilidade com template atual
                'rejected_models': rejected_count,        # Nova convenção
                'models_in_review': review_count,         # Para sidebar
            })
            
            counts_time = time.time() - counts_start
            logger.info(f"Tempo consultas de contagem: {counts_time:.4f}s")
        except Exception as e:
            logger.error(f"Erro ao carregar contagens: {str(e)}")
            context.update({
                'total_models': 0,
                'approved_models_count': 0,
                'approved_models': 0,
                'review_models_count': 0,
                'review_models': 0,
                'in_review': 0,
                'rejected_models': 0,
                'models_in_review': 0,
            })
        
        # Métricas médias dos modelos aprovados
        metrics_start = time.time()
        try:
            approved_models = AIModel.objects.filter(status='approved')
            avg_metrics = {
                'avg_accuracy': 0,
                'avg_precision': 0,
                'avg_recall': 0,
                'avg_f1_score': 0
            }
            
            if approved_models.exists():
                metrics_count = 0
                for model in approved_models:
                    if model.metrics:
                        metrics_count += 1
                        avg_metrics['avg_accuracy'] += model.metrics.get('accuracy', 0) * 100
                        avg_metrics['avg_precision'] += model.metrics.get('precision', 0) * 100
                        avg_metrics['avg_recall'] += model.metrics.get('recall', 0) * 100
                        avg_metrics['avg_f1_score'] += model.metrics.get('f1_score', 0) * 100
                
                if metrics_count > 0:
                    avg_metrics['avg_accuracy'] /= metrics_count
                    avg_metrics['avg_precision'] /= metrics_count
                    avg_metrics['avg_recall'] /= metrics_count
                    avg_metrics['avg_f1_score'] /= metrics_count
            
            context['avg_metrics'] = avg_metrics
            metrics_time = time.time() - metrics_start
            logger.info(f"Tempo cálculo de métricas médias: {metrics_time:.4f}s")
        except Exception as e:
            logger.error(f"Erro ao calcular métricas médias: {str(e)}")
            context['avg_metrics'] = {
                'avg_accuracy': 0,
                'avg_precision': 0,
                'avg_recall': 0,
                'avg_f1_score': 0
            }
        
        # Modelos para revisão - compatibilidade com código existente
        review_start = time.time()
        try:
            models_for_review = AIModel.objects.filter(
                status='review'
            ).select_related('dataset', 'created_by').order_by('-created_at')
            
            context['models_for_review'] = models_for_review
            context['pending_models'] = models_for_review  # Nova convenção
            
            review_time = time.time() - review_start
            logger.info(f"Tempo consulta modelos em revisão: {review_time:.4f}s, Count: {models_for_review.count()}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos em revisão: {str(e)}")
            context['models_for_review'] = []
            context['pending_models'] = []
        
        # Modelos já aprovados/rejeitados - novo no sistema
        approved_start = time.time()
        try:
            # Nova consulta para modelos já processados (aprovados/rejeitados/implantados)
            reviewed_models = AIModel.objects.filter(
                status__in=['approved', 'rejected', 'deployed']
            ).select_related('dataset', 'created_by').order_by('-updated_at')[:20]  # Limitando aos 20 mais recentes
            
            context['reviewed_models'] = reviewed_models
            
            # Manter compatibilidade com código existente
            context['approved_models_list'] = AIModel.objects.filter(
                status='approved'
            ).order_by('-created_at')[:5]
            
            approved_time = time.time() - approved_start
            logger.info(f"Tempo consulta modelos revisados: {approved_time:.4f}s, Count: {reviewed_models.count()}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos revisados: {str(e)}")
            context['reviewed_models'] = []
            context['approved_models_list'] = []
        
        # Para sidebar - compatibilidade com template atual
        sidebar_start = time.time()
        try:
            context['latest_model_for_review'] = (
                AIModel.objects.filter(status='review')
                .order_by('-created_at')
                .first()
            )
            
            context['latest_approved_model'] = (
                AIModel.objects.filter(status='approved')
                .order_by('-updated_at')
                .first()
            )
            
            sidebar_time = time.time() - sidebar_start
            logger.info(f"Tempo consulta modelos para sidebar: {sidebar_time:.4f}s")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos para sidebar: {str(e)}")
            # Não definimos valores default para manter compatibilidade com template
        
        # Adicionar o tempo total
        total_time = time.time() - start_time
        logger.info(f"Tempo total get_context_data: {total_time:.4f}s")
        
        return context

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

# Nova view para API de métricas
class ModelMetricsAPIView(LoginRequiredMixin, ManagerRequiredMixin, View):
    """
    Endpoint de API para fornecer métricas de modelos para o frontend.
    Retorna as métricas em formato JSON para exibição no modal.
    """
    def get(self, request, model_id):
        model = get_object_or_404(AIModel, id=model_id)
        
        # Validação de permissão
        # Apenas gerentes podem ver métricas (garantido pelo ManagerRequiredMixin)
        
        # Se não tiver métricas, retorna objeto vazio
        if not model.metrics:
            return JsonResponse({})
        
        # Retornando as métricas do modelo
        try:
            # As métricas já estão em formato JSON no banco
            return JsonResponse(model.metrics)
        except (TypeError, json.JSONDecodeError):
            # Fallback caso as métricas não estejam em formato válido
            return JsonResponse({
                'error': 'Formato de métrica inválido',
                'message': 'As métricas deste modelo estão em um formato não suportado.'
            })

# Adicionando a view de Approvals que faltava
class ApprovalsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/approvals.html'
    context_object_name = 'pending_models'
    
    def get_queryset(self):
        return AIModel.objects.filter(status='review').order_by('-created_at')

# Nova função review_model para integrar com o dashboard atualizado
def review_model(request, model_id):
    """
    View de função para aprovação/rejeição rápida via dashboard.
    Esta função permite o processamento direto de modelos sem ir para a página detalhada.
    """
    try:
        model = get_object_or_404(AIModel, id=model_id)
        
        if request.method == 'POST':
            # Identificar a ação (approve ou reject)
            decision = request.POST.get('decision')
            
            if decision == 'approve' or decision == 'true':
                success, message = ModelTrainingService.review_model(
                    model.id, True, request.POST.get('review_notes', '')
                )
                if success:
                    messages.success(request, f'Modelo {model.name} aprovado com sucesso!')
                else:
                    messages.error(request, f'Erro na aprovação: {message}')
                    
            elif decision == 'reject' or decision == 'false':
                success, message = ModelTrainingService.review_model(
                    model.id, False, request.POST.get('review_notes', '')
                )
                if success:
                    messages.success(request, f'Modelo {model.name} rejeitado.')
                else:
                    messages.error(request, f'Erro na rejeição: {message}')
            else:
                messages.error(request, 'Decisão inválida. Escolha aprovar ou rejeitar.')
        else:
            messages.error(request, 'Método não permitido. Use POST para esta ação.')
            
    except Exception as e:
        logger.error(f"Erro ao processar revisão do modelo {model_id}: {str(e)}")
        messages.error(request, f'Erro ao processar revisão: {str(e)}')
        
    # Redirecionar de volta para o dashboard em qualquer caso
    return redirect('tenis_admin:manager_dashboard')

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

# Nova função para deploy de modelos
def deploy_model(request, model_id):
    """
    View de função para implantar um modelo aprovado.
    """
    try:
        if request.method == 'POST':
            # Usar o serviço existente ModelDeploymentService para deploy
            success, message = ModelDeploymentService.deploy_model(model_id)
            
            if success:
                messages.success(request, f'Modelo implantado com sucesso!')
            else:
                messages.error(request, f'Erro na implantação: {message}')
        else:
            messages.error(request, 'Método não permitido. Use POST para esta ação.')
            
    except Exception as e:
        logger.error(f"Erro ao implantar modelo {model_id}: {str(e)}")
        messages.error(request, f'Erro ao implantar modelo: {str(e)}')
        
    # Redirecionar de volta para o dashboard em qualquer caso
    return redirect('tenis_admin:manager_dashboard')