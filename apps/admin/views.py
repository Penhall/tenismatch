# /tenismatch/apps/admin/views.py 
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import AIModel, Dataset, ModelMetrics

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

class DatasetUploadView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = Dataset
    template_name = 'analyst/data_upload.html'
    fields = ['name', 'description', 'file']
    success_url = '/admin/analyst/dashboard'

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Dataset enviado com sucesso!')
        return super().form_valid(form)

class ModelTrainingView(LoginRequiredMixin, AnalystRequiredMixin, CreateView):
    model = AIModel
    template_name = 'analyst/training.html'
    fields = ['name', 'version', 'description', 'model_file']
    success_url = '/admin/analyst/dashboard'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        messages.success(self.request, 'Modelo criado e enviado para revisão!')
        return super().form_valid(form)
        
class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = AIModel
    template_name = 'manager/dashboard.html'
    context_object_name = 'models'

    def get_queryset(self):
        return AIModel.objects.filter(status='review')

class ModelReviewView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = AIModel
    template_name = 'manager/model_review.html'
    form_class = ModelReviewForm
    
    def form_valid(self, form):
        model = form.save(commit=False)
        model.status = form.cleaned_data['decision']
        model.save()
        
        if model.status == 'approved':
            messages.success(self.request, 'Modelo aprovado com sucesso!')
            ModelDeploymentService.deploy_model(model.id)
        else:
            messages.warning(self.request, 'Modelo rejeitado.')
            
        return redirect('admin:manager_dashboard')

class MetricsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = ModelMetrics
    template_name = 'manager/metrics.html'
    context_object_name = 'metrics'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['approved_models'] = AIModel.objects.filter(status='approved').count()
        context['total_datasets'] = Dataset.objects.count()
        return context
        
class ModelTrainingDetailView(LoginRequiredMixin, AnalystRequiredMixin, DetailView):
    model = AIModel
    template_name = 'analyst/training_detail.html'
    context_object_name = 'model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_object()
        context['progress'] = model.progress if hasattr(model, 'progress') else 0
        context['training_logs'] = model.get_training_logs()
        return context

class ModelApprovalView(LoginRequiredMixin, ManagerRequiredMixin, View):
    def post(self, request, pk):
        model = get_object_or_404(AIModel, pk=pk)
        action = request.POST.get('action')
        notes = request.POST.get('review_notes', '')

        if action == 'approve':
            model.status = 'approved'
            messages.success(request, 'Modelo aprovado com sucesso!')
        else:
            model.status = 'rejected'
            messages.warning(request, 'Modelo rejeitado.')

        model.review_notes = notes
        model.save()
        return redirect('admin:manager_dashboard')

class DeployModelView(LoginRequiredMixin, ManagerRequiredMixin, View):
    def post(self, request, pk):
        model = get_object_or_404(AIModel, pk=pk)
        try:
            ModelDeploymentService.deploy_model(model.id)
            messages.success(request, 'Modelo implantado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao implantar modelo: {str(e)}')
        return redirect('admin:manager_dashboard')
        
