# /tenismatch/apps/profiles/views.py
from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import UserProfile, ProfileHistory
from .forms import ProfileForm, TennisPreferencesForm  # Adicionado o form correto

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'
    
    def get_object(self, queryset=None):
        # Obtém o perfil do usuário atual
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o histórico recente do perfil
        context['profile_history'] = ProfileHistory.objects.filter(
            profile=self.object
        ).order_by('-timestamp')[:5]  # Últimos 5 registros
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'profiles/edit.html'
    success_url = reverse_lazy('profiles:detail')
    
    def get_object(self, queryset=None):
        # Obtém o perfil do usuário atual
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

class ProfileHistoryView(LoginRequiredMixin, ListView):
    model = ProfileHistory
    template_name = 'profiles/history.html'
    context_object_name = 'history'
    paginate_by = 10
    
    def get_queryset(self):
        # Obtém o histórico do perfil do usuário atual
        profile = get_object_or_404(UserProfile, user=self.request.user)
        return ProfileHistory.objects.filter(profile=profile).order_by('-timestamp')

# Adicionando as classes faltantes
class PreferencesView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = TennisPreferencesForm
    template_name = 'profiles/preferences.html'
    success_url = reverse_lazy('profiles:detail')
    
    def get_object(self, queryset=None):
        # Obtém o perfil do usuário atual
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Preferências atualizadas com sucesso!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(UserProfile, user=self.request.user)
        context['profile'] = profile
        # Adicione mais dados conforme necessário para o dashboard
        return context