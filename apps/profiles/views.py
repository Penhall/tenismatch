# /tenismatch/apps/profiles/views.py 
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm, TennisPreferencesForm

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/edit.html'
    success_url = reverse_lazy('profiles:detail')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

class PreferencesView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'profiles/preferences.html'
    form_class = TennisPreferencesForm
    success_url = reverse_lazy('profiles:detail')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Preferências atualizadas com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileForm(instance=self.get_object())
        return context
