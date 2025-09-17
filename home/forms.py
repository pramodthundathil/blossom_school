# forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email address'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True
    
    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError("Username is required.")
        
        # Check if username contains only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        
        # Check if username is not too short
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        # Check if username is unique (excluding current user)
        existing_user = CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk)
        if existing_user.exists():
            raise ValidationError("This username is already taken.")
        
        return username
    
    def clean_email(self):
        """Validate email address"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email address is required.")
        
        # Check if email is unique (excluding current user)
        existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if existing_user.exists():
            raise ValidationError("This email address is already registered.")
        
        return email.lower()
    
    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        
        if not first_name:
            raise ValidationError("First name is required.")
        
        # Check if name contains only letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', first_name):
            raise ValidationError("First name can only contain letters and spaces.")
        
        return first_name.strip().title()
    
    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        
        if not last_name:
            raise ValidationError("Last name is required.")
        
        # Check if name contains only letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            raise ValidationError("Last name can only contain letters and spaces.")
        
        return last_name.strip().title()


class CustomPasswordChangeForm(PasswordChangeForm):
    """Enhanced password change form with better validation and styling"""
    
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input password-input',
            'placeholder': 'Enter your current password'
        })
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input password-input',
            'placeholder': 'Enter your new password'
        })
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input password-input',
            'placeholder': 'Confirm your new password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text for cleaner form
        for field_name, field in self.fields.items():
            field.help_text = None
    
    def clean_new_password1(self):
        """Enhanced password validation"""
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            raise ValidationError("New password is required.")
        
        # Custom password strength validation
        errors = []
        
        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        
        # Uppercase letter check
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        
        # Lowercase letter check
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        
        # Number check
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number.")
        
        # Special character check
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("Password must contain at least one special character.")
        
        # Check against common passwords
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        if password.lower() in common_passwords:
            errors.append("This password is too common. Please choose a more unique password.")
        
        if errors:
            raise ValidationError(errors)
        
        # Use Django's built-in password validators as well
        try:
            validate_password(password, self.user)
        except ValidationError as e:
            errors.extend(e.messages)
            raise ValidationError(errors)
        
        return password
    
    def clean_new_password2(self):
        """Check that the two password entries match"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if not password2:
            raise ValidationError("Please confirm your new password.")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields do not match.")
        
        return password2
    
    def clean_old_password(self):
        """Validate current password"""
        old_password = self.cleaned_data.get('old_password')
        
        if not old_password:
            raise ValidationError("Current password is required.")
        
        if not self.user.check_password(old_password):
            raise ValidationError("Your current password is incorrect.")
        
        return old_password


class AvatarUploadForm(forms.Form):
    """Form for handling avatar uploads"""
    
    avatar = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-input'
        })
    )
    
    def clean_avatar(self):
        """Validate uploaded avatar"""
        avatar = self.cleaned_data.get('avatar')
        
        if not avatar:
            raise ValidationError("Please select an image to upload.")
        
        # Check file size (max 5MB)
        if avatar.size > 5 * 1024 * 1024:
            raise ValidationError("Image file size must be less than 5MB.")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if avatar.content_type not in allowed_types:
            raise ValidationError("Please upload a valid image file (JPEG, PNG, or GIF).")
        
        # Check image dimensions (optional)
        from PIL import Image
        try:
            img = Image.open(avatar)
            # Check if image is too large
            if img.width > 2000 or img.height > 2000:
                raise ValidationError("Image dimensions must be less than 2000x2000 pixels.")
            
            # Check if image is too small
            if img.width < 50 or img.height < 50:
                raise ValidationError("Image must be at least 50x50 pixels.")
                
        except Exception as e:
            if "Image dimensions" in str(e) or "at least 50x50" in str(e):
                raise e
            raise ValidationError("Invalid image file. Please upload a valid image.")
        
        return avatar