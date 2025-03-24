# /tenismatch/apps/users/context_processors.py

def user_roles(request):
    """
    Adiciona informações de permissão do usuário ao contexto de todos os templates.
    """
    context = {
        'is_analyst': False,
        'is_manager': False,
        'is_premium': False
    }
    
    if request.user.is_authenticated:
        # Verificar papel do usuário
        if hasattr(request.user, 'role'):
            context['is_analyst'] = request.user.role == 'ANALISTA'
            context['is_manager'] = request.user.role == 'GERENTE'
        
        # Verificar se é premium
        if hasattr(request.user, 'is_premium'):
            context['is_premium'] = request.user.is_premium
    
    return context