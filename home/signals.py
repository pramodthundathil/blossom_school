# signals.py (optional - for tracking user activity)
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import CustomUser

@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    """Update user's last login timestamp"""
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

@receiver(post_save, sender=CustomUser)
def user_profile_updated(sender, instance, created, **kwargs):
    """Log when user profile is updated"""
    if not created:
        # You can implement activity logging here
        print(f"User {instance.username} profile updated at {timezone.now()}")
