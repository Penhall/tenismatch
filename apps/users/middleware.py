# middleware.py em apps/users/
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

logger = logging.getLogger(__name__)

class PremiumAccessMiddleware:
   def __init__(self, get_response):
       self.get_response = get_response

   def __call__(self, request):
       if request.user.is_authenticated:
           logger.info(f"Authenticated user {request.user.username} accessing {request.path}")
           premium_paths = ['/premium/', '/chat/', '/search/']
           if any(request.path.startswith(path) for path in premium_paths):
               if not request.user.has_premium_access():
                   logger.warning(f"Non-premium user {request.user.username} attempted to access premium feature: {request.path}")
                   messages.warning(request, 'Esta função requer conta Premium')
                   return redirect('users:upgrade_premium')
       else:
           logger.info(f"Unauthenticated user accessing {request.path}")
       response = self.get_response(request)
       return response
