# /tenismatch/apps/tenis_admin/views.py 
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import AIModel, Dataset
from .forms import DatasetUploadForm, ModelTrainingForm, ModelReviewForm
from .services import ModelTrainingService, ModelDeploymentService

from django.http import HttpResponse
import pandas as pd
from .forms import GenerateDataForm
from apps.matching.ml.dataset import DatasetPreparation

class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Analyst').exists()

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

class AnalystDashboardView(LoginRequiredMixin, AnalystRequiredMixin, ListView):
    model = AIModel
    template_name = 'analyst/dashboard.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = Dataset.objects.filter(uploaded_by=self.request.user)
        return context

class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = 'analyst/data_upload.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Dataset enviado com sucesso!')
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
        ModelTrainingService.train_model(self.object.id, form.cleaned_data['dataset'].id)
        messages.success(self.request, 'Modelo criado e enviado para treinamento!')
        return response

class ModelTrainingDetailView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = AIModel
    template_name = 'analyst/training_detail.html'
    context_object_name = 'model'


class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/dashboard.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(status='review')

class ModelApprovalView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = AIModel
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    success_url = reverse_lazy('tenis_admin:manager_dashboard')

    def form_valid(self, form):
        self.object.status = form.cleaned_data['decision']
        self.object.save()
        
        if self.object.status == 'approved':
            messages.success(self.request, 'Modelo aprovado com sucesso!')
            ModelDeploymentService.deploy_model(self.object.id)
        else:
            messages.warning(self.request, 'Modelo rejeitado.')
            
        return super().form_valid(form)

class ModelCreationView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    form_class = ModelTrainingForm
    template_name = 'analyst/model_creation.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        return super().form_valid(form)

class ModelReviewViewOLD(LoginRequiredMixin, ManagerRequiredMixin, View): # Alterado para View
    model = AIModel
    form_class = ModelReviewForm
    template_name = 'manager/model_review.html'
    success_url = reverse_lazy('tenis_admin:manager_dashboard')

    def get(self, request, *args, **kwargs):
        model = get_object_or_404(AIModel, pk=kwargs['pk'])
        form = ModelReviewForm(instance=model) # Instancia o formulário com a instância do modelo
        return render(request, self.template_name, {'form': form, 'model': model})

    def post(self, request, *args, **kwargs):
        model = get_object_or_404(AIModel, pk=kwargs['pk'])
        form = ModelReviewForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            if form.cleaned_data['decision'] == 'approved':
                messages.success(request, 'Modelo aprovado com sucesso!')
            else:
                messages.warning(request, 'Modelo rejeitado.')
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form, 'model': model})

class DeployModelView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = AIModel
    fields = ['status']
    template_name = 'manager/model_review.html'
    success_url = reverse_lazy('tenis_admin:manager_dashboard')

    def form_valid(self, form):
        self.object.status = 'deployed'
        self.object.save()
        messages.success(self.request, 'Modelo implantado com sucesso!')
        return super().form_valid(form)

class MetricsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/metrics.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.all()

class ApprovalsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/approvals.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(status='review')

class SyntheticDataGeneratorView(LoginRequiredMixin, AnalystRequiredMixin, FormView):
    template_name = 'analyst/generate_data.html'
    form_class = GenerateDataForm
    success_url = reverse_lazy('tenis_admin:dataset_upload')

    def form_valid(self, form):
        n_samples = form.cleaned_data['n_samples']
        dataset_type = form.cleaned_data['dataset_type']
        
        if dataset_type == 'shoes':
            data = generate_shoes_dataset(n_samples)
        elif dataset_type == 'preferences':
            data = generate_preferences_dataset(n_samples)
        
        filename = f"{dataset_type}_dataset_{timezone.now().strftime('%Y%m%d')}.csv"
        df = pd.DataFrame(data)
        
        # Salvar CSV temporariamente
        temp_file = StringIO()
        df.to_csv(temp_file, index=False)
        
        response = HttpResponse(temp_file.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(self.request, f'Dataset gerado com {n_samples} amostras')
        return response


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


class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetUploadForm
    template_name = 'analyst/data_upload.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        
        # Processa o dataset
        success, message = DatasetService.process_dataset(self.object.id)
        if success:
            messages.success(self.request, 'Dataset enviado e processado com sucesso!')
        else:
            messages.error(self.request, message)
            
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = Dataset.objects.filter(
            uploaded_by=self.request.user
        ).order_by('-uploaded_at')
        return context
        
class ModelTrainingView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    form_class = ModelTrainingForm
    template_name = 'analyst/training.html'
    success_url = reverse_lazy('tenis_admin:analyst_dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        response = super().form_valid(form)
        
        # Obter dados de treinamento do dataset
        training_data = DatasetService.get_training_data(form.cleaned_data['dataset'].id)
        
        # Instanciar e treinar o modelo
        trainer = SneakerMatchTraining()
        metrics = trainer.train_model(training_data)
        
        # Salvar métricas
        self.object.metrics = metrics
        self.object.status = 'review'
        self.object.save()
        
        messages.success(self.request, 
            f'Modelo treinado com sucesso! Acurácia: {metrics["accuracy"]:.2%}')
        return response
        
class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = AIModel
    template_name = 'manager/model_review.html'

    def post(self, request, *args, **kwargs):
        model = self.get_object()
        action = request.POST.get('action')
        
        if action == 'approve':
            model.status = 'approved'
            messages.success(request, 'Modelo aprovado com sucesso!')
        else:
            model.status = 'rejected'
            messages.warning(request, 'Modelo rejeitado.')
            
        model.save()
        return redirect('tenis_admin:manager_dashboard')
        
class MetricsDashboardView(LoginRequiredMixin, ManagerRequiredMixin, TemplateView):
    template_name = 'manager/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = int(self.request.GET.get('period', 30))
        
        metrics_service = MetricsService()
        
        # Coleta métricas relacionadas aos modelos
        model_metrics = metrics_service.get_model_performance_metrics(days=period)
        daily_model_metrics = metrics_service.get_daily_model_metrics(days=period)
        
        # Prepara dados para gráficos
        context.update({
            'model_metrics': model_metrics,
            'daily_model_metrics': {
                'dates': [m['date'].strftime('%d/%m') for m in daily_model_metrics],
                'accuracies': [m['avg_accuracy'] for m in daily_model_metrics],
                'precisions': [m['avg_precision'] for m in daily_model_metrics],
                'recalls': [m['avg_recall'] for m in daily_model_metrics],
                'f1_scores': [m['avg_f1_score'] for m in daily_model_metrics]
            }
        })
        
        return context

class ModelPerformanceView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = AIModel
    template_name = 'manager/model_performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_object()
        
        # Aqui você pode adicionar métricas específicas do modelo que não dependam de matches
        # Por exemplo, você pode usar as métricas salvas durante o treinamento do modelo
        
        context.update({
            'accuracy': model.metrics.get('accuracy', 0),
            'precision': model.metrics.get('precision', 0),
            'recall': model.metrics.get('recall', 0),
            'f1_score': model.metrics.get('f1_score', 0),
        })
        
        return context
