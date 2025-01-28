from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class RegularUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role not in ['ANALISTA', 'GERENTE']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == 'ANALISTA':
                return redirect('tenis_admin:analyst_dashboard')
            elif self.request.user.role == 'GERENTE':
                return redirect('tenis_admin:manager_dashboard')
        return redirect('users:login')
