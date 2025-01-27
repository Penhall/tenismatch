from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Analyst').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a Analistas.')
        return redirect('users:login')

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito a Gerentes.')
        return redirect('users:login')