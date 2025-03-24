# /tenismatch/apps/users/middleware.py
from django.urls import resolve
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class UserRoleMiddleware:
    """
    Middleware para gerenciar acesso baseado em roles de usuário.
    Redireciona usuários sem o papel apropriado para suas áreas autorizadas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processar a requisição
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Se o usuário não está autenticado, não precisa verificar role
        if not request.user.is_authenticated:
            return None
        
        try:
            # Obter o namespace atual
            current_url = resolve(request.path)
            namespace = current_url.namespace
            
            # Usuários regulares não devem acessar áreas restritas
            if namespace == 'tenis_admin':
                # Verificar se é analista ou gerente
                if request.user.role not in ['ANALISTA', 'GERENTE']:
                    messages.error(request, 'Você não tem permissão para acessar esta área.')
                    return redirect('users:dashboard')
                
                # Verificar se analista está tentando acessar área de gerente
                if request.user.role == 'ANALISTA' and 'manager' in request.path:
                    messages.error(request, 'Você não tem permissão para acessar a área do gerente.')
                    return redirect('tenis_admin:analyst_dashboard')
                
                # Verificar se gerente está tentando acessar área de analista
                if request.user.role == 'GERENTE' and 'analyst' in request.path:
                    messages.error(request, 'Você não tem permissão para acessar a área do analista.')
                    return redirect('tenis_admin:manager_dashboard')
            
        except Exception as e:
            # Se ocorrer algum erro na resolução da URL, apenas continuar
            pass
        
        return None

class PremiumAccessMiddleware:
    """
    Middleware para verificar acesso a recursos premium.
    Redireciona usuários sem assinatura premium para a página de upgrade.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processar a requisição
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Se o usuário não está autenticado ou a view não tem atributo premium_required, pular
        if not request.user.is_authenticated or not getattr(view_func, 'premium_required', False):
            return None
        
        # Verificar se o usuário tem acesso premium
        if not request.user.has_premium_access():
            messages.warning(request, 'Esta funcionalidade requer uma assinatura premium.')
            return redirect('users:premium')
        
        return None