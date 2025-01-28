# /tenismatch/apps/users/views.py 
# apps/users/views.py
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .models import User
from .forms import CustomUserCreationForm, UserUpdateForm
from apps.matching.models import Match

class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Add user-specific data here that doesn't involve matches
        return context

def landing_page(request):
    return render(request, 'landing.html')
    
def about(request):
    return render(request, 'about.html')

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_approved = False
        user.role = 'ANALISTA'
        user.save()
        return super().form_valid(form)

class ApproveAnalystView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'GERENTE':
            return redirect('home')
        unapproved_analysts = User.objects.filter(role='ANALISTA', is_approved=False)
        return render(request, 'users/approve_analysts.html', {'analysts': unapproved_analysts})

    def post(self, request):
        if request.user.role != 'GERENTE':
            return redirect('home')
        analyst_id = request.POST.get('analyst_id')
        if analyst_id:
            analyst = User.objects.get(id=analyst_id)
            analyst.is_approved = True
            analyst.save()
        return redirect('users:approve_analysts')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'ANALISTA':
            if user.is_approved:
                return reverse_lazy('tenis_admin:analyst_dashboard')
            else:
                return reverse_lazy('users:login')  # Redirect back to login with a message
        elif user.role == 'GERENTE':
            return reverse_lazy('tenis_admin:manager_dashboard')
        elif user.is_staff:
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('users:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        if user.role == 'ANALISTA' and not user.is_approved:
            form.add_error(None, "Sua conta ainda não foi aprovada.")
            return self.form_invalid(form)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class CustomLogoutView(LogoutView):
    next_page = '/'

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profiles:detail')
    
class SignUpPremiumView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'signup_premium.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_premium = True
        user.premium_until = timezone.now() + timedelta(days=30)
        user.save()
        return super().form_valid(form)

class UpgradePremiumView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user.is_premium = True
        user.premium_until = timezone.now() + timedelta(days=30)
        user.save()
        messages.success(request, 'Conta atualizada para Premium!')
        return redirect('profiles:detail')
