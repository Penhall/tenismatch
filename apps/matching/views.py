# /tenismatch/apps/matching/views.py 
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import SneakerProfile, Match
from .forms import SneakerProfileForm
from .services.recommender import TenisMatchRecommender
from .models import Match, MatchFeedback
from .forms import MatchFeedbackForm
from django.shortcuts import get_object_or_404, redirect
from apps.users.mixins import RegularUserRequiredMixin

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
            recommender = TenisMatchRecommender()
            matches = recommender.get_recommendations(user_profile)
            return [match[0] for match in matches]
        except SneakerProfile.DoesNotExist:
            messages.warning(self.request, 'Complete seu perfil de tênis primeiro!')
            return []

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
