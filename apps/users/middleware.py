# /tenismatch/apps/users/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class PremiumAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            premium_paths = ['/premium/', '/chat/', '/search/']
            
            # Verifica se o caminho atual requer premium
            if any(request.path.startswith(path) for path in premium_paths):
                if not request.user.is_premium:
                    messages.warning(request, 'Esta função requer conta Premium')
                    return redirect('users:upgrade_premium')
        
        return self.get_response(request)