from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import * 
from .models import * 
from home.decorators import unauthenticated_user
from payments.models import PaymentPlan, Payment, PaymentInstallment, PaymentItem, PaymentReminder


from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
import logging
import json
from django.db.models import Sum, Q, F


# Set up logging
logger = logging.getLogger(__name__)


@unauthenticated_user
def student_list(request):
    students = Student.objects.all()

    context = {
        "students":students
    }
    return render(request,'students/all-students.html',context)



@unauthenticated_user
@csrf_protect
@require_http_methods(["GET", "POST"])
def student_create(request):
    """
    Create a new student with enhanced validation and AJAX support
    """
    if request.method == 'POST':
        # Check if request is AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        logger.info(f"POST request received. Is AJAX: {is_ajax}")
        logger.debug(f"POST data keys: {list(request.POST.keys())}")
        logger.debug(f"FILES data keys: {list(request.FILES.keys())}")
        
        form = StudentForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Use database transaction to ensure data integrity
                with transaction.atomic():
                    # Create student instance without saving
                    student = form.save(commit=False)
                    
                    # Set the created_by field if user is authenticated
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        student.created_by = request.user
                    
                    # Set default year of admission if not provided
                    if not student.year_of_admission:
                        student.year_of_admission = datetime.now().year
                    
                    # Calculate age at enrollment if date of birth is provided and age is not set
                    if student.date_of_birth and not student.age_at_enrollment:
                        today = datetime.now().date()
                        age = today.year - student.date_of_birth.year
                        if today.month < student.date_of_birth.month or \
                           (today.month == student.date_of_birth.month and today.day < student.date_of_birth.day):
                            age -= 1
                        if 1 <= age <= 18:
                            student.age_at_enrollment = age
                    
                    # Auto-populate primary email if not provided
                    if not student.email:
                        if student.father_email:
                            student.email = student.father_email
                        elif student.mother_email:
                            student.email = student.mother_email
                    
                    # Auto-populate primary phone if not provided
                    if not student.phone_number:
                        if student.father_mobile:
                            student.phone_number = student.father_mobile
                        elif student.mother_mobile:
                            student.phone_number = student.mother_mobile
                    
                    # Set default status
                    if not student.status:
                        student.status = 'enrolled'
                    
                    # Save the student
                    student.save()
                    
                    logger.info(f"Student saved successfully: {student.get_full_name()} (ID: {student.student_id})")
                    
                    if is_ajax:
                        # messages.success(
                        #     request, 
                        #     f"Student {student.get_full_name()} (ID: {student.student_id}) created successfully."
                        # )
                        # return redirect('student_detail', pk=student.id )
                        return JsonResponse({
                            'success': True,
                            'message': f'Student {student.get_full_name()} has been registered successfully!',
                            'redirect_url': reverse('create_payment_plan', kwargs={'student_id': student.id}),
                            'student_id': str(student.pk),
                            'student_name': student.get_full_name(),
                            'student_number': student.student_id
                        }, status=200)
                    else:
                        messages.success(
                            request, 
                            f"Student {student.get_full_name()} (ID: {student.student_id}) created successfully."
                        )
                        return redirect('create_payment_plan', student_id=student.id )
                        
            except ValidationError as e:
                logger.warning(f"Validation error during student creation: {e}")
                error_message = str(e) if hasattr(e, 'message') else 'Validation error occurred.'
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'Validation error occurred.',
                        'errors': {'__all__': [error_message]}
                    }, status=400)
                else:
                    messages.error(request, f"Validation error: {error_message}")
                    
            except Exception as e:
                logger.error(f"Unexpected error during student creation: {e}", exc_info=True)
                error_message = "An unexpected error occurred while creating the student."
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': {'__all__': [str(e)]}
                    }, status=500)
                else:
                    messages.error(request, f"An error occurred: {str(e)}")
        else:
            # Form has validation errors
            logger.warning(f"Form validation failed. Errors: {form.errors}")
            
            if is_ajax:
                # Format errors for JSON response
                errors = {}
                for field, field_errors in form.errors.items():
                    errors[field] = [str(error) for error in field_errors]
                
                # Include non-field errors
                if form.non_field_errors():
                    errors['__all__'] = [str(error) for error in form.non_field_errors()]
                
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': errors,
                    'form_errors': True
                }, status=400)
            else:
                messages.error(request, "Please correct the errors below.")
    
    else:
        # GET request - show empty form
        form = StudentForm()
        
        # Pre-populate some fields with sensible defaults
        form.fields['year_of_admission'].initial = datetime.now().year
        form.fields['city'].initial = 'Dubai'
    
    # Prepare context for template
    context = {
        'form': form,
        'title': 'Add New Student',
        'submit_text': 'Register Student',
        'current_year': datetime.now().year,
        'form_errors': form.errors if request.method == 'POST' else None
    }
    
    return render(request, 'students/student_form.html', context)


@csrf_protect
def student_validate_field(request):
    """
    AJAX endpoint for real-time field validation
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value')
        
        if not field_name:
            return JsonResponse({'error': 'Field name is required'}, status=400)
        
        try:
            # Create a temporary form instance with just this field for validation
            form_data = {field_name: field_value}
            form = StudentForm(data=form_data)
            
            # Validate the entire form to trigger clean methods
            form.is_valid()
            
            # Get errors for the specific field
            field_errors = form.errors.get(field_name, [])
            
            response_data = {
                'valid': len(field_errors) == 0,
                'errors': field_errors,
                'field_name': field_name
            }
            
            # Add specific validation messages for better UX
            if len(field_errors) == 0 and field_value:
                response_data['message'] = 'Valid'
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error in field validation: {e}", exc_info=True)
            return JsonResponse({
                'valid': False, 
                'errors': ['Validation error occurred'],
                'field_name': field_name
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def validate_student_data(cleaned_data):
    """
    Custom validation for student data - for additional business logic
    """
    errors = {}
    
    # Validate age consistency
    if cleaned_data.get('date_of_birth') and cleaned_data.get('age_at_enrollment'):
        birth_date = cleaned_data['date_of_birth']
        provided_age = cleaned_data['age_at_enrollment']
        
        today = datetime.now().date()
        calculated_age = today.year - birth_date.year
        if today.month < birth_date.month or \
           (today.month == birth_date.month and today.day < birth_date.day):
            calculated_age -= 1
        
        if abs(calculated_age - provided_age) > 1:
            errors['age_at_enrollment'] = ['Age does not match the date of birth provided.']
    
    # Validate contact information
    contact_fields = ['father_mobile', 'mother_mobile', 'home_telephone', 'phone_number']
    has_contact = any(cleaned_data.get(field) for field in contact_fields)
    
    if not has_contact:
        errors['father_mobile'] = ['At least one contact number must be provided.']
    
    # Validate email addresses
    email_fields = ['father_email', 'mother_email', 'email']
    has_email = any(cleaned_data.get(field) for field in email_fields)
    
    if not has_email:
        errors['father_email'] = ['At least one email address must be provided.']
    
    # Validate emergency contact
    first_contact_person = cleaned_data.get('first_contact_person')
    first_contact_telephone = cleaned_data.get('first_contact_telephone')
    
    if first_contact_person and not first_contact_telephone:
        errors['first_contact_telephone'] = ['Phone number is required when emergency contact person is provided.']
    
    # Check for duplicate students (same name + DOB)
    if cleaned_data.get('first_name') and cleaned_data.get('last_name') and cleaned_data.get('date_of_birth'):
        existing_student = Student.objects.filter(
            first_name__iexact=cleaned_data['first_name'],
            last_name__iexact=cleaned_data['last_name'],
            date_of_birth=cleaned_data['date_of_birth']
        ).first()
        
        if existing_student:
            errors['__all__'] = [
                f'A student with the same name and date of birth already exists (ID: {existing_student.student_id}). '
                'Please verify the details or contact administration.'
            ]
    
    return errors


@csrf_protect
def student_check_duplicate(request):
    """
    AJAX endpoint to check for duplicate students
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        date_of_birth = request.POST.get('date_of_birth')
        
        if first_name and last_name and date_of_birth:
            try:
                # Parse date
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                
                # Check for existing student
                existing_student = Student.objects.filter(
                    first_name__iexact=first_name,
                    last_name__iexact=last_name,
                    date_of_birth=dob
                ).first()
                
                if existing_student:
                    return JsonResponse({
                        'duplicate_found': True,
                        'message': f'A student with similar details already exists (ID: {existing_student.student_id})',
                        'student_id': existing_student.student_id,
                        'student_name': existing_student.get_full_name()
                    })
                else:
                    return JsonResponse({
                        'duplicate_found': False,
                        'message': 'No duplicate found'
                    })
                    
            except ValueError:
                return JsonResponse({
                    'error': 'Invalid date format'
                }, status=400)
        else:
            return JsonResponse({
                'error': 'First name, last name, and date of birth are required'
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Utility functions for better form processing

def clean_phone_number(phone_number):
    """Clean and validate phone number"""
    if not phone_number:
        return phone_number
    
    # Remove extra spaces and format consistently
    cleaned = ' '.join(phone_number.split())
    return cleaned


def generate_student_preview(form_data):
    """Generate a preview of student data for confirmation"""
    preview = {
        'full_name': f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip(),
        'age': form_data.get('age_at_enrollment'),
        'nationality': form_data.get('nationality'),
        'parents': {
            'father': form_data.get('father_name'),
            'mother': form_data.get('mother_name')
        },
        'contact': {
            'email': form_data.get('email') or form_data.get('father_email') or form_data.get('mother_email'),
            'phone': form_data.get('phone_number') or form_data.get('father_mobile') or form_data.get('mother_mobile')
        }
    }
    return preview


def log_student_creation_attempt(request, form_data, success=False, errors=None):
    """Log student creation attempts for debugging and analytics"""
    log_data = {
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'student_name': f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip(),
        'errors': errors
    }
    
    if success:
        logger.info(f"Student creation successful: {json.dumps(log_data)}")
    else:
        logger.warning(f"Student creation failed: {json.dumps(log_data)}")


# Custom form class with enhanced validation
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class EnhancedStudentForm(StudentForm):
    """
    Enhanced student form with better validation and widgets
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add custom validators
        phone_validator = RegexValidator(
            regex=r'^[\+]?[\d\s\-\(\)]+$',
            message='Please enter a valid phone number.'
        )
        
        # Apply phone validator to phone fields
        phone_fields = [
            'father_mobile', 'father_work_telephone', 'mother_mobile', 
            'mother_work_telephone', 'home_telephone', 'first_contact_telephone',
            'second_contact_telephone', 'phone_number'
        ]
        
        for field_name in phone_fields:
            if field_name in self.fields:
                self.fields[field_name].validators.append(phone_validator)
        
        # Set current year as default for year_of_admission
        current_year = datetime.now().year
        self.fields['year_of_admission'].initial = current_year
        
        # Add help text for certain fields
        self.fields['child_photo'].help_text = 'Accepted formats: JPEG, PNG, GIF, WEBP. Max size: 5MB'
        self.fields['date_of_birth'].help_text = 'Age will be calculated automatically'
        self.fields['languages_spoken'].help_text = 'List all languages the child can speak, separated by commas'
    
    def clean_child_emirates_id(self):
        """Validate Emirates ID format if provided"""
        emirates_id = self.cleaned_data.get('child_emirates_id')
        if emirates_id:
            # Remove spaces and hyphens
            emirates_id = emirates_id.replace(' ', '').replace('-', '')
            if not emirates_id.isdigit() or len(emirates_id) != 15:
                raise ValidationError('Emirates ID must be 15 digits long.')
        return emirates_id
    
    def clean_email(self):
        """Ensure primary email is provided if parent emails are empty"""
        email = self.cleaned_data.get('email')
        father_email = self.cleaned_data.get('father_email')
        mother_email = self.cleaned_data.get('mother_email')
        
        if not email and not father_email and not mother_email:
            raise ValidationError('At least one email address must be provided.')
        
        return email
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        
        # Validate date consistency
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')
        
        if date_start and date_end and date_start >= date_end:
            raise ValidationError('End date must be after start date.')
        
        # Validate age and date of birth consistency
        date_of_birth = cleaned_data.get('date_of_birth')
        age_at_enrollment = cleaned_data.get('age_at_enrollment')
        
        if date_of_birth and age_at_enrollment:
            today = datetime.now().date()
            calculated_age = today.year - date_of_birth.year
            if today.month < date_of_birth.month or \
               (today.month == date_of_birth.month and today.day < date_of_birth.day):
                calculated_age -= 1
            
            if abs(calculated_age - age_at_enrollment) > 1:
                raise ValidationError('Age at enrollment does not match the date of birth.')
        
        return cleaned_data

@unauthenticated_user
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    document_form = DocumentForm()
    initial_data = {}
    initial_data['student'] = student
    form = TransportationForm(initial=initial_data)

    """Show detailed payment information for a student"""
    
    # Get payment plans
    payment_plans = PaymentPlan.objects.filter(student=student).order_by('-academic_year')
    
    # Get all payments
    payments = Payment.objects.filter(student=student).order_by('-payment_date')
    
    # Get outstanding installments
    outstanding_installments = PaymentInstallment.objects.filter(
        payment_plan__student=student,
        status__in=['pending', 'overdue', 'partially_paid']
    ).order_by('due_date')
    
    # Calculate totals
    total_paid = payments.filter(payment_status='completed').aggregate(
        Sum('net_amount')
    )['net_amount__sum'] or 0
    
    total_outstanding = sum(inst.get_outstanding_amount() for inst in outstanding_installments)

    context = {
        'student': student,
        'payment_plans': payment_plans,
        'payments': payments,
        'outstanding_installments': outstanding_installments,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        "document_form":document_form,
        "form":form
    }
    
    return render(request, 'students/student_detail.html', context)

@unauthenticated_user
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form_update.html', {'form': form})

@unauthenticated_user
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if student.child_photo:
        student.child_photo.delete()
    if student.father_photo:
        student.father_photo.delete()
    if student.mother_photo:
        student.mother_photo.delete()
    student.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect('students')


@unauthenticated_user
def disable_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.is_active = False
    student.status = "withdrawn"
    student.save()
    messages.success(request, "Student disabled.")
    return redirect('student_detail', pk=pk)

@unauthenticated_user
def enable_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.is_active = True
    student.status = "enrolled"
    student.save()
    messages.success(request, "Student enabled.")
    return redirect('student_detail', pk=pk)

@unauthenticated_user
def upload_document(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student

            document.uploaded_by = request.user
            document.save()
            messages.success(request, "Document uploaded.")
            return redirect('student_detail', pk=pk)
    else:
        form = DocumentForm()
    return render(request, 'students/upload_document.html', {'form': form, 'student': student})

@unauthenticated_user
def delete_document(request, pk):
    document = get_object_or_404(StudentDocument, pk=pk)
    
    document.delete()
    messages.success(request, "Document deleted.")
    return redirect('student_detail', pk=pk)
    

@unauthenticated_user
def bulk_action(request):
    # Implement bulk action logic here
    messages.success(request, "Bulk action completed.")
    return redirect('student_list')

@unauthenticated_user
def export_students(request):
    # Implement export logic here
    messages.success(request, "Students exported.")
    return redirect('student_list')

@unauthenticated_user
def search_students_ajax(request):
    # Implement AJAX search logic here
    return render(request, 'students/search_results.html')

@unauthenticated_user
def student_stats_ajax(request):
    # Implement AJAX stats logic here
    return render(request, 'students/student_stats.html')


# notes add update 
@unauthenticated_user 
def add_notes(request, pk):
    student = get_object_or_404(Student, id = pk)
    if request.method == "POST":
        notes = request.POST['notes']
        note = StudentNote.objects.create(student = student, note = notes)
        note.save()
        messages.success(request,"Note Created........")
        return redirect("student_detail", pk = pk)


@unauthenticated_user
def delete_notes(request, pk):
    note = get_object_or_404(StudentNote, id = pk)
    student = note.student
    note.delete()
    messages.success(request,"Note deleted........")
    return redirect("student_detail", pk = student.id)


@unauthenticated_user
def add_transportation(request, student_id):
    student = get_object_or_404(Student, id = student_id)
    transportation_qs = student.transportation.all()
    transportation = transportation_qs.first() if transportation_qs.exists() else None

    if transportation:
        # transportation =  student.transportation.objects.all()[0]
        if request.method == 'POST':
            form = TransportationForm(request.POST, instance = transportation)
            if form.is_valid():
                form.save()
                messages.success(request, "Transportation details Updated successfully.")
                return redirect("student_detail",pk = student_id)

        else:
            initial_data = {}
            if student_id:
                student = Student.objects.get(pk=student_id)
                initial_data['student'] = student
            form = TransportationForm(initial=initial_data)
    else: 
        if request.method == 'POST':
            form = TransportationForm(request.POST)
            if form.is_valid():
                trans = form.save(commit=False)
                trans.student = student
                trans.save()
                messages.success(request, "Transportation details added successfully.")
                return redirect("student_detail",pk = student_id)
        else:
            initial_data = {}
            if student_id:
                student = Student.objects.get(pk=student_id)
                initial_data['student'] = student
            form = TransportationForm(initial=initial_data)

            return redirect("student_detail",pk = student_id)


# notifications 

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Notification
from django.views.decorators.csrf import csrf_exempt


@login_required
def notification_list(request):
    """Display all notifications with filtering options"""
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    notifications = Notification.objects.filter(user=request.user).select_related(
        'student', 'installment', 'installment__payment_plan'
    )
    
    # Apply filters
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'upcoming':
        notifications = notifications.filter(notification_type='upcoming')
    elif filter_type == 'overdue':
        notifications = notifications.filter(notification_type='overdue')
    # 'all' shows everything
    
    # Get unread count
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Pagination
    paginator = Paginator(notifications, 20)  # 20 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'unread_count': unread_count,
        'filter_type': filter_type,
    }
    
    return render(request, 'notifications/notification_list.html', context)


@login_required
@csrf_exempt
def mark_notification_read(request, pk):
    """Mark a single notification as read (AJAX endpoint)"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(Notification, pk=pk, user=request.user)
            notification.mark_as_read()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
@csrf_exempt
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user (AJAX endpoint)"""
    if request.method == 'POST':
        try:
            updated_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            return JsonResponse({'success': True, 'count': updated_count})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
@csrf_exempt
def get_unread_notification_count(request):
    """Get count of unread notifications (AJAX endpoint)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
@csrf_exempt
def delete_notification(request, pk):
    """Delete a notification (AJAX endpoint)"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(Notification, pk=pk, user=request.user)
            notification.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)