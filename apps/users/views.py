# /tenismatch/apps/users/views.py 
# apps/users/views.py
from datetime import timedelta
from django.utils import timezone
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from .forms import CustomUserCreationForm, UserUpdateForm

def landing_page(request):
    return render(request, 'landing.html')
    
def about(request):
    return render(request, 'about.html')

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        # Verificar grupos para redirecionar para dashboards corretos
        groups = user.groups.all()
        if groups.filter(name='Analyst').exists():
            return reverse_lazy('tenis_admin:analyst_dashboard')
        elif groups.filter(name='Manager').exists():
            return reverse_lazy('tenis_admin:manager_dashboard')
        elif user.is_staff:
            return reverse_lazy('admin:index') # Dashboard admin padrão se não for analista/gerente
        else:
            # Redirecionar para o perfil para usuários normais
            return reverse_lazy('profiles:detail')

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
