# utils.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io
import base64

def resize_image(image_file, max_size=(800, 800), quality=85):
    """Resize image while maintaining aspect ratio"""
    try:
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Calculate new dimensions while maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read())
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

def generate_avatar_url(user):
    """Generate avatar URL or return default"""
    if hasattr(user, 'avatar') and user.avatar:
        return user.avatar.url
    return None

def validate_password_strength(password):
    """Validate password strength and return score"""
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Uppercase check
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter")
    
    # Lowercase check
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter")
    
    # Number check
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add at least one number")
    
    # Special character check
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
    else:
        feedback.append("Add at least one special character")
    
    # Determine strength level
    if score <= 1:
        strength = "Very Weak"
    elif score == 2:
        strength = "Weak"
    elif score == 3:
        strength = "Fair"
    elif score == 4:
        strength = "Good"
    else:
        strength = "Strong"
    
    return {
        'score': score,
        'max_score': 5,
        'strength': strength,
        'feedback': feedback,
        'percentage': (score / 5) * 100
    }


# admin.py (enhanced admin interface for CustomUser)
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     """Enhanced admin interface for CustomUser"""
    
#     list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
#     list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     ordering = ('-date_joined',)
    
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {
#             'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions'),
#         }),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
    
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
#         }),
#     )
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related()

# middleware.py (optional - for activity tracking)


# serializers.py (for API endpoints if needed)
# from rest_framework import serializers
# from .models import CustomUser

# class UserProfileSerializer(serializers.ModelSerializer):
#     """Serializer for user profile API"""
    
#     full_name = serializers.SerializerMethodField()
#     initials = serializers.SerializerMethodField()
    
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'full_name', 'initials']
#         read_only_fields = ['id', 'date_joined', 'full_name', 'initials']
    
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}".strip()
    
#     def get_initials(self, obj):
#         if obj.first_name and obj.last_name:
#             return f"{obj.first_name[0]}{obj.last_name[0]}".upper()
#         return obj.username[:2].upper()
    
#     def validate_email(self, value):
#         """Validate email uniqueness"""
#         if CustomUser.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
#             raise serializers.ValidationError("This email is already registered.")
#         return value.lower()
    
#     def validate_username(self, value):
#         """Validate username uniqueness"""
#         if CustomUser.objects.filter(username=value).exclude(pk=self.instance.pk if self.instance else None).exists():
#             raise serializers.ValidationError("This username is already taken.")
#         return value

