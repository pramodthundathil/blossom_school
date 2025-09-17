from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

class UserActivityMiddleware:
    """Middleware to track user activity"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Update last activity for authenticated users
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            # You can implement last_activity tracking here
            # request.user.last_activity = timezone.now()
            # request.user.save(update_fields=['last_activity'])
            pass
        
        return response