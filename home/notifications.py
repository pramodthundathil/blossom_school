# utils/notifications.py

from django.contrib.auth.models import User
from students.models import Notification

from django.utils import timezone

class NotificationManager:
    """Helper class for managing notifications"""

    @staticmethod
    def get_unread_count():
        """Get count of unread notifications for a user"""
        return Notification.objects.filter( is_read=False).count()

    @staticmethod
    def get_recent_notifications(limit=10):
        """Get recent notifications for a user"""
        return Notification.objects.all().order_by('-created_at')[:limit]

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        Notification.objects.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )

    @staticmethod
    def get_notifications_by_type(user, notification_type, is_read=None):
        """Get notifications filtered by type and read status"""
        queryset = Notification.objects.filter( notification_type=notification_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        return queryset.order_by('-created_at')

    @staticmethod
    def delete_old_notifications(days=90):
        """Delete notifications older than specified days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()
        return deleted_count


# Context processor for notifications (add to settings.py)
def notification_context(request):
    """Add notification count to all templates"""
    if request.user.is_authenticated:
        return {
            'unread_notification_count': NotificationManager.get_unread_count(),
            'recent_notifications': NotificationManager.get_recent_notifications(limit=5)
        }
    return {}