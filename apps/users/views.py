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
    success_url = reverse_lazy('users:approval_waiting')

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_approved = False
            user.role = 'ANALISTA'
            user.save()
            logger.info(f"New user created: {user.username}, role: {user.role}")
            messages.success(self.request, 'Cadastro realizado com sucesso. Aguarde a aprovação do administrador.')
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error creating new user: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid signup form: {form.errors}")
        return super().form_invalid(form)

class ApprovalWaitingView(TemplateView):
    template_name = 'users/approval_waiting.html'

class ApproveAnalystView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'GERENTE':
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect('home')
        unapproved_analysts = User.objects.filter(role='ANALISTA', is_approved=False).order_by('-date_joined')
        return render(request, 'users/approve_analysts.html', {'analysts': unapproved_analysts})

    def post(self, request):
        if request.user.role != 'GERENTE':
            messages.error(request, "Você não tem permissão para realizar esta ação.")
            return redirect('home')
        analyst_id = request.POST.get('analyst_id')
        if analyst_id:
            try:
                analyst = User.objects.get(id=analyst_id, role='ANALISTA', is_approved=False)
                analyst.is_approved = True
                analyst.save()
                messages.success(request, f"O analista {analyst.username} foi aprovado com sucesso.")
                # Aqui você pode adicionar lógica para enviar um e-mail ao analista informando que sua conta foi aprovada
            except User.DoesNotExist:
                messages.error(request, "Analista não encontrado ou já aprovado.")
        else:
            messages.error(request, "ID do analista não fornecido.")
        return redirect('users:approve_analysts')

import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        logger.info(f"Getting success URL for user {user.username}. Role: {user.role}, Is approved: {user.is_approved}")
        if user.role == 'ANALISTA':
            if user.is_approved:
                url = reverse_lazy('tenis_admin:analyst_dashboard')
            else:
                logger.warning(f"Unapproved analyst {user.username} attempted to log in")
                url = reverse_lazy('users:approval_waiting')
        elif user.role == 'GERENTE':
            url = reverse_lazy('tenis_admin:manager_dashboard')
        elif user.is_staff:
            url = reverse_lazy('admin:index')
        else:
            url = reverse_lazy('users:dashboard')
        logger.info(f"Redirecting user {user.username} to {url}")
        return url

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"Login form is valid for user: {user.username}, Role: {user.role}, Is approved: {user.is_approved}")
        login(self.request, user)
        logger.info(f"User {user.username} authenticated successfully")
        success_url = self.get_success_url()
        logger.info(f"Redirecting authenticated user {user.username} to {success_url}")
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        logger.warning(f"Failed login attempt for username: {form.data.get('username')}")
        errors = form.errors.as_data()
        for field, error_list in errors.items():
            for error in error_list:
                logger.warning(f"Form error in field {field}: {error}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        logger.info(f"GET request to login page from user: {request.user}")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info(f"POST request to login page from user: {request.user}")
        return super().post(request, *args, **kwargs)

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
