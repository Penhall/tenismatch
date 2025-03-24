# /tenismatch/apps/profiles/views.py
from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import UserProfile, ProfileHistory
from .forms import ProfileForm, TennisPreferencesForm
import logging

logger = logging.getLogger(__name__)

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
        logger.debug(f"ProfileUpdateView.form_valid chamado para perfil_id: {self.object.id}")
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

class PreferencesView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = TennisPreferencesForm
    template_name = 'profiles/preferences.html'
    success_url = reverse_lazy('profiles:detail')
    
    def get_object(self, queryset=None):
        # Obtém o perfil do usuário atual
        profile = get_object_or_404(UserProfile, user=self.request.user)
        logger.debug(f"PreferencesView.get_object: Recuperado perfil {profile.id}")
        return profile
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        logger.debug(f"PreferencesView.get_form_kwargs: {kwargs}")
        return kwargs
    
    def form_valid(self, form):
        logger.debug(f"PreferencesView.form_valid chamado com dados: {form.cleaned_data}")
        
        # Garantir que os campos JSON não sejam None
        self.object.preferred_brands = self.object.preferred_brands or []
        self.object.style_preferences = self.object.style_preferences or {}
        
        # Salva o formulário explicitamente com commit=True
        self.object = form.save(commit=True)
        
        # Verifique se os dados foram realmente salvos
        refreshed_profile = UserProfile.objects.get(pk=self.object.pk)
        logger.debug(f"Após salvar - preferred_brands: {refreshed_profile.preferred_brands}")
        logger.debug(f"Após salvar - style_preferences: {refreshed_profile.style_preferences}")
        
        messages.success(self.request, 'Preferências atualizadas com sucesso!')
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        logger.warning(f"PreferencesView.form_invalid chamado. Erros: {form.errors}")
        messages.error(self.request, 'Erro ao atualizar preferências. Verifique os campos e tente novamente.')
        return super().form_invalid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(UserProfile, user=self.request.user)
        context['profile'] = profile
        
        # Adicione informações para o dashboard
        context['matches_count'] = 0  # Substituir pela contagem real
        context['favorite_matches_count'] = 0  # Substituir pela contagem real
        context['preferred_brands_count'] = len(profile.preferred_brands) if profile.preferred_brands else 0
        
        # Contar cores preferidas
        favorite_colors = profile.style_preferences.get('favorite_colors', []) if profile.style_preferences else []
        context['preferred_colors_count'] = len(favorite_colors)
        
        # Matches recentes (substituir por dados reais)
        context['latest_matches'] = []
        context['favorite_matches'] = []
        
        return context