# /tenismatch/apps/matching/views.py 
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import SneakerProfile, Match
from .forms import SneakerProfileForm
from .services.recommender import TenisMatchRecommender

class SneakerFormView(LoginRequiredMixin, CreateView):
    model = SneakerProfile
    form_class = SneakerProfileForm
    template_name = 'matching/sneaker_form.html'
    success_url = '/matching/matches/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Perfil do tênis atualizado com sucesso!')
        return super().form_valid(form)

class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matching/match_list.html'
    context_object_name = 'matches'

    def get_queryset(self):
        try:
            user_profile = self.request.user.sneakerprofile
            recommender = TenisMatchRecommender()
            matches = recommender.get_recommendations(user_profile)
            return [match[0] for match in matches]
        except SneakerProfile.DoesNotExist:
            messages.warning(self.request, 'Complete seu perfil de tênis primeiro!')
            return []

class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'matching/match_detail.html'
    context_object_name = 'match'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.get_object()
        
        if not self.request.user.is_premium and match.user_b != self.request.user:
            context['limited_view'] = True
            
        recommender = TenisMatchRecommender()
        context['common_interests'] = recommender.get_common_interests(
            match.user_a.sneakerprofile,
            match.user_b.sneakerprofile
        )
        return context