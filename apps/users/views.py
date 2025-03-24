# /tenismatch/apps/users/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import User
from apps.profiles.models import UserProfile
from apps.matching.models import SneakerProfile

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

class LandingView(TemplateView):
    template_name = 'landing.html'

class AboutView(TemplateView):
    template_name = 'about.html'

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('users:dashboard')

class SignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm  # Alterado de UserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conta criada com sucesso! Agora você pode fazer login.')
        return response

# Adicionando as classes que estavam faltando
class SignupPremiumView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup_premium.html'  # Ajustado para usar o template na raiz
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_premium = True
        user.premium_until = timezone.now() + timezone.timedelta(days=30)
        user.save()
        messages.success(self.request, 'Conta premium criada com sucesso! Aproveite seus benefícios.')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    View para o dashboard principal do usuário.
    Exibe informações da conta, perfil, preferências de tênis e ações disponíveis.
    """
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter perfil de usuário, se existir
        try:
            context['user_profile'] = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            context['user_profile'] = None
            
        # Obter perfil de tênis, se existir
        try:
            context['sneaker_profile'] = SneakerProfile.objects.get(user=self.request.user)
        except SneakerProfile.DoesNotExist:
            context['sneaker_profile'] = None
        
        # Adicionar estatísticas e dados adicionais
        from apps.matching.models import Match
        context['matches_count'] = Match.objects.filter(user_a=self.request.user).count()
        context['mutual_matches_count'] = Match.objects.filter(
            user_a=self.request.user, 
            is_mutual=True
        ).count()
        
        # Verificar se o usuário é premium e quando expira (se aplicável)
        if self.request.user.is_premium and self.request.user.premium_until:
            context['premium_days_left'] = (self.request.user.premium_until - timezone.now()).days
        
        return context

class UpgradePremiumView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/premium.html')
    
    def post(self, request):
        user = request.user
        user.is_premium = True
        user.premium_until = timezone.now() + timezone.timedelta(days=30)
        user.save()
        messages.success(request, 'Sua conta foi atualizada para Premium com sucesso!')
        return redirect('users:dashboard')

class PremiumInfoView(TemplateView):
    template_name = 'users/premium.html'

class ApproveAnalystsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/approve_analysts.html'
    context_object_name = 'analysts'
    
    def test_func(self):
        # Usar role em vez de grupo
        return self.request.user.role == 'GERENTE'
    
    def get_queryset(self):
        # Usar role em vez de grupo
        return User.objects.filter(role='ANALISTA', is_active=False)
    
    def post(self, request):
        analyst_id = request.POST.get('analyst_id')
        if analyst_id:
            analyst = User.objects.get(id=analyst_id)
            analyst.is_active = True
            analyst.save()
            messages.success(request, f'Analista {analyst.username} aprovado com sucesso!')
        return redirect('users:approve_analysts')

class ApprovalWaitingView(TemplateView):
    template_name = 'users/approval_waiting.html'