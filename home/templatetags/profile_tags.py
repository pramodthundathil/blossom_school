# Custom template tags (templatetags/profile_tags.py)
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def user_avatar(user, size=40):
    """Generate user avatar HTML"""
    if hasattr(user, 'avatar') and user.avatar:
        return format_html(
            '<img src="{}" alt="{}" class="user-avatar" style="width: {}px; height: {}px; border-radius: 50%; object-fit: cover;">',
            user.avatar.url, user.get_full_name() or user.username, size, size
        )
    else:
        initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper() if user.first_name and user.last_name else user.username[:2].upper()
        return format_html(
            '<div class="user-avatar-fallback" style="width: {}px; height: {}px; border-radius: 50%; background: var(--e-global-color-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: {}px;">{}</div>',
            size, size, size//3, initials
        )

@register.filter
def role_badge_class(role):
    """Return CSS class for role badge"""
    role_classes = {
        'admin': 'role-admin',
        'account': 'role-account',
        'user': 'role-user',
    }
    return role_classes.get(role, 'role-user')

@register.filter
def password_strength_color(score):
    """Return color for password strength"""
    if score <= 1:
        return '#FF6B6B'
    elif score == 2:
        return '#FF9587'
    elif score == 3:
        return '#FFD700'
    elif score == 4:
        return '#4ECDC4'
    else:
        return '#43A574'