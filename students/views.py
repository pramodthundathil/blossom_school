# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import csv

from .models import Student, Parent, EmergencyContact, Document
from .forms import (
    StudentForm, ParentFormSet, EmergencyContactFormSet, DocumentFormSet,
    StudentSearchForm, DisableStudentForm, DocumentForm
)
from home.decorators import unauthenticated_user


@unauthenticated_user
def student_list(request):
    """Display all students with search and filter functionality"""
    students = Student.objects.select_related().prefetch_related('parents')
    
    # Search functionality
    search = request.GET.get('search')
    status = request.GET.get('status')
    year_group = request.GET.get('year_group')
    is_active = request.GET.get('is_active')
    
    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(student_id__icontains=search) |
            Q(email__icontains=search)
        )
    
    if status:
        students = students.filter(status=status)
    
    if year_group:
        students = students.filter(year_group=year_group)
    
    if is_active == 'true':
        students = students.filter(is_active=True)
    elif is_active == 'false':
        students = students.filter(is_active=False)
    
    students = students.order_by('-created_at')
    
    context = {
        'students': students,
        'search_form': StudentSearchForm(request.GET),
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(is_active=True).count(),
        'pending_applications': Student.objects.filter(status='pending').count(),
    }
    
    return render(request, 'students/all-students.html', context)


@unauthenticated_user
def student_detail(request, pk):
    """Display detailed view of a student"""
    print(f"quirylodedd,{pk}")
    student = get_object_or_404(Student, pk=pk)
    
    context = {
        'student': student,
        'parents': student.parents.all(),
        'emergency_contacts': student.emergency_contacts.all().order_by('priority'),
        'documents': student.documents.all().order_by('-uploaded_at'),
    }
    
    return render(request, 'students/student_detail.html', context)


@unauthenticated_user
def student_create(request):
    """Create a new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        parent_formset = ParentFormSet(request.POST)
        emergency_formset = EmergencyContactFormSet(request.POST)
        document_formset = DocumentFormSet(request.POST, request.FILES)
        
        if form.is_valid() and parent_formset.is_valid() and emergency_formset.is_valid() and document_formset.is_valid():
            with transaction.atomic():
                form.instance.created_by = request.user
                student = form.save()
                
                parent_formset.instance = student
                parent_formset.save()
                
                emergency_formset.instance = student
                emergency_formset.save()
                
                document_formset.instance = student
                for doc_form in document_formset:
                    if doc_form.cleaned_data and not doc_form.cleaned_data.get('DELETE'):
                        if doc_form.instance.pk is None:
                            doc_form.instance.uploaded_by = request.user
                document_formset.save()
            
            messages.success(request, f'Student {student.get_full_name()} has been created successfully.')
            return redirect('student_detail', pk=student.pk)
        else:
            print(f'Some ting Wrong {form.errors.as_text}, {parent_formset.errors}, {emergency_formset.errors} {document_formset.errors}')
            messages.error(request, f'Some ting Wrong {form.errors.as_text}, {parent_formset.errors}, {emergency_formset.errors} {document_formset.errors}')
            return redirect("student_create")
    else:
        form = StudentForm()
        parent_formset = ParentFormSet()
        emergency_formset = EmergencyContactFormSet()
        document_formset = DocumentFormSet()
    
    context = {
        'form': form,
        'parent_formset': parent_formset,
        'emergency_formset': emergency_formset,
        'document_formset': document_formset,
        'form_title': 'Add New Student',
        'submit_text': 'Create Student',
    }
    
    return render(request, 'students/student_form.html', context)


@unauthenticated_user
def student_update(request, pk):
    """Update an existing student"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        parent_formset = ParentFormSet(request.POST, instance=student)
        emergency_formset = EmergencyContactFormSet(request.POST, instance=student)
        document_formset = DocumentFormSet(request.POST, request.FILES, instance=student)
        
        if form.is_valid() and parent_formset.is_valid() and emergency_formset.is_valid() and document_formset.is_valid():
            with transaction.atomic():
                student = form.save()
                
                parent_formset.instance = student
                parent_formset.save()
                
                emergency_formset.instance = student
                emergency_formset.save()
                
                document_formset.instance = student
                for doc_form in document_formset:
                    if doc_form.cleaned_data and not doc_form.cleaned_data.get('DELETE'):
                        if doc_form.instance.pk is None:
                            doc_form.instance.uploaded_by = request.user
                document_formset.save()
            
            messages.success(request, f'Student {student.get_full_name()} has been updated successfully.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
        parent_formset = ParentFormSet(instance=student)
        emergency_formset = EmergencyContactFormSet(instance=student)
        document_formset = DocumentFormSet(instance=student)
    
    context = {
        'form': form,
        'parent_formset': parent_formset,
        'emergency_formset': emergency_formset,
        'document_formset': document_formset,
        'student': student,
        'form_title': f'Edit Student: {student.get_full_name()}',
        'submit_text': 'Update Student',
    }
    
    return render(request, 'students/student_form.html', context)


@unauthenticated_user
def student_delete(request, pk):
    """Disable a student instead of deleting"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        # Instead of deleting, disable the student
        student.status = 'disabled'
        student.is_active = False
        student.save()
        
        messages.success(request, f'Student {student.get_full_name()} has been disabled.')
        return redirect('students')
    
    return render(request, 'students/student_confirm_delete.html', {'student': student})


@unauthenticated_user
def disable_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = DisableStudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.get_full_name()} has been disabled.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = DisableStudentForm(instance=student)
    
    return render(request, 'students/disable_student.html', {
        'form': form,
        'student': student
    })


@unauthenticated_user
def enable_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if student.status == 'disabled':
        student.status = 'pending'
        student.is_active = True
        student.save()
        messages.success(request, f'Student {student.get_full_name()} has been enabled.')
    else:
        messages.warning(request, f'Student {student.get_full_name()} is not disabled.')
    
    return redirect('student_detail', pk=student.pk)


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
            messages.success(request, 'Document uploaded successfully.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = DocumentForm()
    
    return render(request, 'students/upload_document.html', {
        'form': form,
        'student': student
    })


@unauthenticated_user
def delete_document(request, pk, doc_pk):
    student = get_object_or_404(Student, pk=pk)
    document = get_object_or_404(Document, pk=doc_pk, student=student)
    
    if request.method == 'POST':
        document_name = document.name
        document.delete()
        messages.success(request, f'Document "{document_name}" has been deleted.')
        return redirect('student_detail', pk=student.pk)
    
    return render(request, 'students/confirm_delete_document.html', {
        'student': student,
        'document': document
    })


@unauthenticated_user
def student_dashboard(request):
    """Dashboard with statistics and recent activities"""
    context = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(is_active=True).count(),
        'pending_applications': Student.objects.filter(status='pending').count(),
        'accepted_students': Student.objects.filter(status='accepted').count(),
        'enrolled_students': Student.objects.filter(status='enrolled').count(),
        'disabled_students': Student.objects.filter(status='disabled').count(),
        
        'recent_students': Student.objects.select_related().order_by('-created_at')[:10],
        'recent_documents': Document.objects.select_related('student').order_by('-uploaded_at')[:10],
        
        # Year group statistics
        'year_group_stats': {
            choice[1]: Student.objects.filter(year_group=choice[0], is_active=True).count()
            for choice in Student.YEAR_GROUP_CHOICES
        },
        
        # Status statistics
        'status_stats': {
            choice[1]: Student.objects.filter(status=choice[0]).count()
            for choice in Student.STATUS_CHOICES
        }
    }
    
    return render(request, 'students/dashboard.html', context)


@require_POST
@unauthenticated_user
def bulk_action(request):
    """Handle bulk actions on students"""
    action = request.POST.get('action')
    student_ids = request.POST.getlist('student_ids')
    
    if not student_ids:
        messages.error(request, 'No students selected.')
        return redirect('students')
    
    students = Student.objects.filter(pk__in=student_ids)
    
    if action == 'enable':
        students.update(is_active=True, status='pending')
        messages.success(request, f'{len(student_ids)} students have been enabled.')
    
    elif action == 'disable':
        students.update(is_active=False, status='disabled')
        messages.success(request, f'{len(student_ids)} students have been disabled.')
    
    elif action == 'accept':
        students.update(status='accepted')
        messages.success(request, f'{len(student_ids)} students have been accepted.')
    
    elif action == 'reject':
        students.update(status='rejected')
        messages.success(request, f'{len(student_ids)} applications have been rejected.')
    
    elif action == 'enroll':
        students.update(status='enrolled')
        messages.success(request, f'{len(student_ids)} students have been enrolled.')
    
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('students')


@unauthenticated_user
def export_students(request):
    """Export students data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'First Name', 'Last Name', 'Date of Birth', 'Gender',
        'Email', 'Phone', 'Year Group', 'Status', 'City', 'Postcode',
        'Nationality', 'Created Date'
    ])
    
    students = Student.objects.all().order_by('student_id')
    for student in students:
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.date_of_birth,
            student.get_gender_display(),
            student.email,
            student.phone_number,
            student.get_year_group_display(),
            student.get_status_display(),
            student.city,
            student.postcode,
            student.nationality,
            student.created_at.strftime('%Y-%m-%d')
        ])
    
    return response


# AJAX Views for dynamic functionality
@unauthenticated_user
def search_students_ajax(request):
    """AJAX endpoint for student search autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'students': []})
    
    students = Student.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(student_id__icontains=query)
    )[:10]
    
    results = [{
        'id': student.pk,
        'text': f"{student.get_full_name()} ({student.student_id})",
        'student_id': student.student_id,
        'status': student.get_status_display()
    } for student in students]
    
    return JsonResponse({'students': results})


@unauthenticated_user
def student_stats_ajax(request):
    """AJAX endpoint for dashboard statistics"""
    stats = {
        'total': Student.objects.count(),
        'active': Student.objects.filter(is_active=True).count(),
        'pending': Student.objects.filter(status='pending').count(),
        'accepted': Student.objects.filter(status='accepted').count(),
        'enrolled': Student.objects.filter(status='enrolled').count(),
        'disabled': Student.objects.filter(status='disabled').count(),
    }
    
    return JsonResponse(stats)