# /tenismatch/apps/users/mixins.py
import time
import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger('tenismatch')

class RegularUserRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar se o usuário é um usuário regular (não analista ou gerente)
    """
    def test_func(self):
        start_time = time.time()
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        try:
            # Verifica se o usuário NÃO é analista ou gerente
            result = not (user.is_analyst() or user.is_manager())
            
            elapsed_time = time.time() - start_time
            if elapsed_time > 0.1:
                logger.warning(f"Verificação de usuário regular lenta: {elapsed_time:.4f}s para o usuário {user.username}")
                
            return result
        except Exception as e:
            logger.error(f"Erro ao verificar permissão de usuário regular: {str(e)}")
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, "Acesso restrito a usuários regulares.")
        return redirect('users:dashboard')