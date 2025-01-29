import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

class RegularUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        is_regular = user.is_authenticated and user.role not in ['ANALISTA', 'GERENTE']
        logger.info(f"User {user.username} tested for regular user access: {'Passed' if is_regular else 'Failed'}")
        return is_regular

    def handle_no_permission(self):
        user = self.request.user
        if user.is_authenticated:
            logger.warning(f"Authenticated user {user.username} with role {user.role} attempted to access regular user area")
            if user.role == 'ANALISTA':
                return redirect('tenis_admin:analyst_dashboard')
            elif user.role == 'GERENTE':
                return redirect('tenis_admin:manager_dashboard')
        else:
            logger.warning("Unauthenticated user attempted to access regular user area")
        return redirect('users:login')
