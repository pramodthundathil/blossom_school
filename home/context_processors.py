# context_processors.py
from django.contrib.auth.models import AnonymousUser

def user_context(request):
    """Add user-related context variables to all templates"""
    if isinstance(request.user, AnonymousUser):
        return {}
    
    return {
        'user_full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
        'user_initials': f"{request.user.first_name[:1]}{request.user.last_name[:1]}".upper() if request.user.first_name and request.user.last_name else request.user.username[:2].upper(),
        'user_role_display': request.user.role.title() if hasattr(request.user, 'role') else 'User',
    }

