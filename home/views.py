from django.shortcuts import render, redirect, get_object_or_404 
"""
This module contains view functions for the home application of the Blossom School project.
Functions:
    - index(request): Renders the index (home) page of the application.
    - login(request): Handles user authentication and logs the user in.
    - logout(request): Logs the user out and redirects to the appropriate page.
    - authenticate(request): Authenticates user credentials for login.
Imports:
    - Django shortcuts for rendering templates, redirecting, and retrieving objects.
    - Django messages framework for displaying notifications.
    - Django authentication decorators and functions for managing user sessions.
    - Local models and forms for handling application-specific data and user input.
"""
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from .models import *
from .forms import *
from .decorators import unauthenticated_user

# authentications and dashboards 

@unauthenticated_user
def index(request):
    return render(request,"auth_templates/index.html")


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect("index")
        else:
            messages.error(request, "username or password incorrect")
            return redirect('signin')
    return render(request,"auth_templates/login.html")

def signout(request):
    logout(request)
    return redirect("signin")

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import base64
import os
from PIL import Image
import io
from .forms import ProfileUpdateForm, CustomPasswordChangeForm
from .decorators import unauthenticated_user

@unauthenticated_user
def profile(request):
    """Display user profile page"""
    context = {
        'user': request.user,
        'profile_form': ProfileUpdateForm(instance=request.user),
        'password_form': CustomPasswordChangeForm(user=request.user),
    }
    return render(request, 'auth_templates/profile.html', context)

@unauthenticated_user
def update_profile(request):
    """Handle profile information updates"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            # messages.success(request, 'Profile updated successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully!'
                })
            
            return redirect('profile')
        else:
            # Handle form errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            error_message = '; '.join(error_messages)
            messages.error(request, f'Error updating profile: {error_message}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': error_message
                })
    
    return redirect('profile')

@unauthenticated_user
def change_password(request):
    """Handle password change requests"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(data=request.POST, user=request.user)
        
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            # messages.success(request, 'Password updated successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Password updated successfully!'
                })
            
            return redirect('profile')
        else:
            # Handle form errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            error_message = '; '.join(error_messages)
            # messages.error(request, f'Error changing password: {error_message}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': error_message
                })
    
    return redirect('profile')

@unauthenticated_user
@csrf_exempt
def upload_avatar(request):
    """Handle avatar image uploads with proper file handling"""
    if request.method == 'POST':
        try:
            # Handle regular file upload
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if avatar_file.content_type not in allowed_types:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please upload a valid image file (JPEG, PNG, or GIF)'
                    })
                
                # Validate file size (max 5MB)
                if avatar_file.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'message': 'File size must be less than 5MB'
                    })
                
                try:
                    # Process image with PIL for validation and optimization
                    image = Image.open(avatar_file)
                    
                    # Validate image dimensions
                    if image.width > 2000 or image.height > 2000:
                        return JsonResponse({
                            'success': False,
                            'message': 'Image dimensions must be less than 2000x2000 pixels'
                        })
                    
                    if image.width < 50 or image.height < 50:
                        return JsonResponse({
                            'success': False,
                            'message': 'Image must be at least 50x50 pixels'
                        })
                    
                    # Convert to RGB if necessary (for JPEG)
                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Resize if too large (maintain aspect ratio)
                    max_size = (800, 800)
                    if image.width > max_size[0] or image.height > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save processed image to memory
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format='JPEG', quality=85, optimize=True)
                    img_buffer.seek(0)
                    
                    # Create a new ContentFile with processed image
                    processed_file = ContentFile(img_buffer.read())
                    
                    # Generate unique filename
                    file_extension = 'jpg'  # Always save as JPEG after processing
                    file_name = f'avatars/user_{request.user.id}_avatar.{file_extension}'
                    
                    # Remove old avatar if exists
                    if hasattr(request.user, 'avatar') and request.user.avatar:
                        try:
                            default_storage.delete(request.user.avatar.name)
                        except:
                            pass  # Ignore if file doesn't exist
                    
                    # Save new file
                    saved_path = default_storage.save(file_name, processed_file)
                    
                    # Update user model (assuming you have an avatar field)
                    # If you don't have an avatar field in your user model, you'll need to add it
                    # or create a separate UserProfile model with avatar field
                    try:
                        request.user.avatar = saved_path
                        request.user.save()
                    except Exception as e:
                        # If avatar field doesn't exist, just return success without saving to model
                        pass
                    
                    return JsonResponse({
                        'success': True,
                        'avatar_url': default_storage.url(saved_path),
                        'message': 'Avatar updated successfully!'
                    })
                    
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error processing image: {str(e)}'
                    })
            
            # Handle base64 image data from JavaScript (if needed for future use)
            elif 'avatar_data' in request.POST:
                try:
                    image_data = request.POST['avatar_data']
                    # Remove data:image/jpeg;base64, prefix
                    format_info, imgstr = image_data.split(';base64,') 
                    ext = format_info.split('/')[-1]
                    
                    # Decode base64 image
                    img_data = base64.b64decode(imgstr)
                    
                    # Process with PIL
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Same processing as above
                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    max_size = (800, 800)
                    if image.width > max_size[0] or image.height > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format='JPEG', quality=85, optimize=True)
                    img_buffer.seek(0)
                    
                    processed_file = ContentFile(img_buffer.read())
                    file_name = f'avatars/user_{request.user.id}_avatar.jpg'
                    
                    # Remove old avatar
                    if hasattr(request.user, 'avatar') and request.user.avatar:
                        try:
                            default_storage.delete(request.user.avatar.name)
                        except:
                            pass
                    
                    saved_path = default_storage.save(file_name, processed_file)
                    
                    try:
                        request.user.avatar = saved_path
                        request.user.save()
                    except:
                        pass
                    
                    return JsonResponse({
                        'success': True,
                        'avatar_url': default_storage.url(saved_path),
                        'message': 'Avatar updated successfully!'
                    })
                    
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error processing base64 image: {str(e)}'
                    })
            
            return JsonResponse({
                'success': False,
                'message': 'No image data received'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error uploading avatar: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@unauthenticated_user
def get_user_activity(request):
    """Get user activity data for the profile page"""
    # This is a placeholder - implement based on your activity tracking needs
    activities = [
        {
            'type': 'login',
            'title': 'Last Login',
            'time': request.user.last_login.strftime('%B %d, %Y at %I:%M %p') if request.user.last_login else 'Never',
            'icon': 'fas fa-sign-in-alt'
        },
        {
            'type': 'update',
            'title': 'Profile Created',
            'time': request.user.date_joined.strftime('%B %d, %Y'),
            'icon': 'fas fa-user-edit'
        },
        {
            'type': 'security',
            'title': 'Account Status',
            'time': 'Active' if request.user.is_active else 'Inactive',
            'icon': 'fas fa-shield-alt'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'activities': activities
    })




# settings for school
# 
# 
# 
#  

#site setting and class room Update

@unauthenticated_user 
def site_setting(request):
    class_rooms = ClassRooms.objects.all().order_by('-id')
    fee_category = FeeCategory.objects.all().order_by("-id")
    if request.method == "POST":
        try:
            name = request.POST['class_room']
            class_room = ClassRooms.objects.create(class_name = name, created_by = request.user)
            class_room.save()
            messages.success(request, "Class room saved successfully...")
        except:
            messages.info(request, 'Something wrong....')

        return redirect("site_setting")
    else:
        context = {"class_rooms":class_rooms,"fee_category":fee_category}
        return render(request,"settings/settings.html",context)
    
@unauthenticated_user
def update_class(request, pk):
    class_room = get_object_or_404(ClassRooms, id = pk)
    if request.method == "POST":
        name = request.POST['class_room']
        class_room.class_name = name 
        class_room.save()
        messages.info(request, 'Class Updated.....')
    return redirect("site_setting")

@unauthenticated_user
def delete_class(request, pk):
    class_room = get_object_or_404(ClassRooms, id = pk)
    class_room.delete()
    messages.info(request,"Class room deleted success.....")
    return redirect(site_setting)

#Fee category Section
@unauthenticated_user
def fee_category(request):
    if request.method == "POST":
        try:
            name = request.POST['name']
            fee_cat = FeeCategory.objects.create(name = name)
            fee_cat.save()
            messages.success(request, "Fee Category saved successfully...")
        except:
            messages.info(request, 'Something wrong....')

        return redirect("site_setting")
    return redirect("site_setting")


@unauthenticated_user
def update_fee_category(request, pk):
    cat = get_object_or_404(FeeCategory, id = pk)
    if request.method == "POST":
        name = request.POST['name']
        cat.name = name 
        cat.save()
        messages.info(request, 'Fee Category Updated.....')
    return redirect("site_setting")


@unauthenticated_user
def delete_fee_category(request, pk):
    cat = get_object_or_404(FeeCategory, id = pk)
    cat.delete()
    messages.info(request,"Fee Category deleted success.....")
    return redirect("site_setting")
    