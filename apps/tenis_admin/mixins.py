# /tenismatch/apps/tenis_admin/mixins.py
import logging
import time
from django.contrib.auth.mixins import UserPassesTestMixin

logger = logging.getLogger('tenismatch')

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        # Verificação direta do campo role - mais rápida e eficiente
        return user.role == 'GERENTE'


class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        # Verificação direta do campo role - mais rápida e eficiente
        return user.role == 'ANALISTA'