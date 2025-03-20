# /tenismatch/apps/tenis_admin/middleware.py
import time
import logging
from django.urls import resolve

logger = logging.getLogger('tenismatch')


class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        start_time = time.time()
        path = request.path
        
        # Log antes do processamento
        if 'manager' in path.lower() or (
            hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'GERENTE'
        ):
            logger.info(f"[Gerente] Iniciando requisição: {request.method} {path}")
        
        # Processar a requisição
        response = self.get_response(request)
        
        # Calcular o tempo total
        duration = time.time() - start_time
        
        # Log para requisições de gerente
        if 'manager' in path.lower() or (
            hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'GERENTE'
        ):
            logger.info(f"[Gerente] Requisição {request.method} {path} completada em {duration:.4f}s")
        
        # Log para requisições lentas (acima de 0.5 segundo)
        if duration > 0.5:
            logger.warning(f"Requisição lenta: {request.method} {path} - {duration:.2f}s")
            
        # Log para requisições de login
        if '/login/' in path and request.method == 'POST':
            username = request.POST.get('username', 'desconhecido')
            logger.info(f"Login processado para {username} em {duration:.2f} segundos")
            
        return response