# /tenismatch/apps/matching/views.py
from django.views.generic import CreateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render  # Adicionado import do renderfrom django.contrib import messages
from django.http import JsonResponse
import logging

from .models import SneakerProfile, Match, MatchFeedback
from .forms import SneakerProfileForm, MatchFeedbackForm
# Substituir o import antigo pelo novo
from .services import RecommenderService, MatchStatisticsService
from apps.users.mixins import RegularUserRequiredMixin

logger = logging.getLogger(__name__)

class SneakerFormView(LoginRequiredMixin, RegularUserRequiredMixin, CreateView):
    model = SneakerProfile
    form_class = SneakerProfileForm
    template_name = 'matching/sneaker_form.html'
    success_url = '/matching/matches/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Perfil do tênis atualizado com sucesso!')
        return super().form_valid(form)

class MatchListView(LoginRequiredMixin, RegularUserRequiredMixin, ListView):
    model = Match
    template_name = 'matching/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        try:
            user_profile = self.request.user.sneakerprofile
            # Usar novo serviço de recomendação
            recommender = RecommenderService()
            recommendations = recommender.get_matches(user_profile)
            
            # Converter para o formato esperado pelo código anterior (lista de perfis)
            # O código anterior esperava uma lista de tuplas (match, score)
            # E então extraia apenas o 'match' com [match[0] for match in matches]
            return [rec['profile'] for rec in recommendations]
        except SneakerProfile.DoesNotExist:
            messages.warning(self.request, 'Complete seu perfil de tênis primeiro!')
            return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_profile = self.request.user.sneakerprofile
            recommender = RecommenderService()
            recommendations = recommender.get_matches(user_profile)
            
            # Adicionar dados completos de recomendações ao contexto
            # Isso permite que o template acesse informações adicionais como razões
            context['recommendations'] = recommendations
        except Exception as e:
            logger.error(f"Erro ao obter recomendações: {str(e)}")
            
        return context

class MatchDetailView(LoginRequiredMixin, RegularUserRequiredMixin, DetailView):
    model = Match
    template_name = 'matching/match_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_form'] = MatchFeedbackForm()
        context['existing_feedback'] = MatchFeedback.objects.filter(
            user=self.request.user,
            match=self.object
        ).first()
        
        # Adicionar informações de compatibilidade usando o novo serviço
        try:
            user_profile = self.request.user.sneakerprofile
            other_profile = self.object.user_b.sneakerprofile
            
            recommender = RecommenderService()
            compatibility_info = recommender.get_single_match(user_profile, other_profile)
            context['compatibility_info'] = compatibility_info
        except Exception as e:
            logger.error(f"Erro ao obter informações de compatibilidade: {str(e)}")
            
        return context

class MatchFeedbackView(LoginRequiredMixin, RegularUserRequiredMixin, CreateView):
    model = MatchFeedback
    form_class = MatchFeedbackForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        match = get_object_or_404(Match, pk=self.kwargs['match_id'])
        
        # Verifica se já existe feedback
        existing_feedback = MatchFeedback.objects.filter(
            user=self.request.user,
            match=match
        ).first()
        
        if existing_feedback:
            # Atualiza feedback existente
            existing_feedback.rating = form.cleaned_data['rating']
            existing_feedback.feedback_text = form.cleaned_data['feedback_text']
            existing_feedback.save()
            messages.success(self.request, 'Feedback atualizado com sucesso!')
        else:
            # Cria novo feedback
            feedback = form.save(commit=False)
            feedback.user = self.request.user
            feedback.match = match
            feedback.save()
            messages.success(self.request, 'Feedback enviado com sucesso!')
            
        return redirect('matching:match_detail', pk=match.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao enviar feedback. Por favor, tente novamente.')
        return redirect('matching:match_detail', pk=self.kwargs['match_id'])

# Adicionando novas views que estavam na nossa implementação

class DailyMatchesView(LoginRequiredMixin, RegularUserRequiredMixin, ListView):
    """
    Exibe sugestões diárias de matches.
    """
    template_name = 'matching/daily_matches.html'
    context_object_name = 'matches'
    
    def get_queryset(self):
        user_profile = self.request.user.sneakerprofile
        
        # Usar o serviço de recomendação para obter sugestões diárias
        recommender = RecommenderService()
        return recommender.get_match_suggestions(user_profile, limit=3)

class MatchStatisticsView(LoginRequiredMixin, RegularUserRequiredMixin, View):
    """
    Exibe estatísticas sobre os matches do usuário.
    """
    def get(self, request):
        user = request.user
        
        # Usar o serviço de estatísticas
        stats = MatchStatisticsService.get_user_match_statistics(user)
        style_distribution = MatchStatisticsService.get_style_distribution()
        recent_history = MatchStatisticsService.get_user_matching_history(user, limit=5)
        
        return render(request, 'matching/statistics.html', {
            'stats': stats,
            'style_distribution': style_distribution,
            'recent_history': recent_history
        })

def update_match_status(request, match_id, status):
    """
    Atualiza o status de um match (liked, rejected, blocked).
    """
    match = get_object_or_404(Match, id=match_id, user_a=request.user)
    
    # Usar o serviço de recomendação para atualizar status
    recommender = RecommenderService()
    user_profile = request.user.sneakerprofile
    
    success, message, is_mutual = recommender.update_match_status(
        user_profile, match.user_b.id, status
    )
    
    if success:
        messages.success(request, message)
        if is_mutual:
            messages.success(request, "Você tem um novo match mútuo!")
    else:
        messages.error(request, message)
    
    return redirect('matching:match_list')

def api_get_matches(request):
    """
    API para obter matches via AJAX.
    """
    user_profile = request.user.sneakerprofile
    
    # Usar o serviço de recomendação
    recommender = RecommenderService()
    matches = recommender.get_matches(user_profile, limit=5)
    
    # Formatar dados para JSON
    matches_data = []
    for match in matches:
        profile = match['profile']
        matches_data.append({
            'id': profile.id,
            'username': profile.user.username,
            'compatibility': match.get('adjusted_score', match.get('compatibility', 0)) * 100,
            'reasons': match.get('reasons', []),
            'profile_url': f"/profiles/{profile.id}/"
        })
    
    return JsonResponse({'matches': matches_data})