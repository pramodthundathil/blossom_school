from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Teacher
from .forms import TeacherForm
from Finance.models import Expense
from home.decorators import unauthenticated_user



# staff functionalities 

@unauthenticated_user
def teacher_list(request):
    """Display list of all teachers"""
    teachers = Teacher.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        teachers = teachers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(teacher_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    context = {
        'teachers': teachers,
        'search_query': search_query
    }
    return render(request, 'teachers/teacher_list.html', context)

@unauthenticated_user
def teacher_create(request):
    """Create a new teacher"""
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            if form.is_valid():
                teacher = form.save()
                messages.success(request,"Staff Created")
                return JsonResponse({
                    'success': True,
                    'message': 'Teacher registered successfully!',
                    'redirect_url': f'/teachers/{teacher.pk}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Please fix the errors in the form.'
                }, status=400)
        else:
            # Regular form submission
            if form.is_valid():
                teacher = form.save()
                messages.success(request, f'Teacher {teacher.full_name} registered successfully!')
                return redirect('teacher_detail', pk=teacher.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherForm()
    
    context = {
        'form': form,
        'title': 'Add New Teacher/Staff'
    }
    return render(request, 'teachers/teacher_form.html', context)

@unauthenticated_user
def teacher_detail(request, pk):
    """Display teacher details"""
    teacher = get_object_or_404(Teacher, pk=pk)
    context = {
        'teacher': teacher
    }
    return render(request, 'teachers/teacher_detail.html', context)

@unauthenticated_user
def teacher_update(request, pk):
    """Update teacher information"""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            if form.is_valid():
                teacher = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Teacher information updated successfully!',
                    'redirect_url': f'/teachers/{teacher.pk}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Please fix the errors in the form.'
                }, status=400)
        else:
            # Regular form submission
            if form.is_valid():
                teacher = form.save()
                messages.success(request, f'Teacher {teacher.full_name} updated successfully!')
                return redirect('teacher_detail', pk=teacher.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherForm(instance=teacher)
    
    context = {
        'form': form,
        'teacher': teacher,
        'title': f'Edit {teacher.full_name}'
    }
    return render(request, 'teachers/teacher_form.html', context)

@unauthenticated_user
@require_http_methods(["POST"])
def teacher_delete(request, pk):
    """Delete a teacher"""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher_name = teacher.full_name
    teacher.delete()
    messages.success(request, f'Teacher {teacher_name} has been deleted.')
    return redirect('teacher_list')

@unauthenticated_user
def disable_teacher(request, pk):
    """Disable a teacher account"""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = False
    teacher.status = 'on_leave'
    teacher.save()
    messages.success(request, f'Teacher {teacher.full_name} has been disabled.')
    return redirect('teacher_list')

@unauthenticated_user
def enable_teacher(request, pk):
    """Enable a teacher account"""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = True
    if teacher.is_on_probation():
        teacher.status = 'on_probation'
    else:
        teacher.status = 'active'
    teacher.save()
    messages.success(request, f'Teacher {teacher.full_name} has been enabled.')
    return redirect('teacher_list')

@unauthenticated_user
@require_http_methods(["POST"])
def bulk_action_teachers(request):
    """Handle bulk actions for teachers"""
    action = request.POST.get('action')
    teacher_ids = request.POST.getlist('teacher_ids[]')
    
    if not action or not teacher_ids:
        messages.error(request, 'Invalid bulk action request.')
        return redirect('teacher_list')
    
    teachers = Teacher.objects.filter(id__in=teacher_ids)
    
    if action == 'delete':
        count = teachers.count()
        teachers.delete()
        messages.success(request, f'{count} teacher(s) deleted successfully.')
    elif action == 'disable':
        teachers.update(is_active=False, status='on_leave')
        messages.success(request, f'{teachers.count()} teacher(s) disabled successfully.')
    elif action == 'enable':
        for teacher in teachers:
            teacher.is_active = True
            if teacher.is_on_probation():
                teacher.status = 'on_probation'
            else:
                teacher.status = 'active'
            teacher.save()
        messages.success(request, f'{teachers.count()} teacher(s) enabled successfully.')
    
    return redirect('teacher_list')



# attendance and salary 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Teacher, Attendance, MonthlySalary
from .forms import (
    AttendanceForm, 
    BulkAttendanceForm, 
    MonthlyAttendanceFilterForm,
    SalaryCalculationForm
)

# ==================== ATTENDANCE VIEWS ====================
@unauthenticated_user
def attendance_dashboard(request):
    """Dashboard showing attendance overview"""
    today = timezone.now().date()
    
    # Get all active teachers
    active_teachers = Teacher.objects.filter(is_active=True, status='active')
    
    # Today's attendance summary
    today_attendance = Attendance.objects.filter(date=today)
    today_present = today_attendance.filter(status='present').count()
    today_absent = today_attendance.filter(status='absent').count()
    today_half_day = today_attendance.filter(status='half_day').count()
    
    # Current month summary
    current_month = today.month
    current_year = today.year
    month_attendance = Attendance.objects.filter(
        date__month=current_month,
        date__year=current_year
    )
    
    context = {
        'today': today,
        'active_teachers_count': active_teachers.count(),
        'today_present': today_present,
        'today_absent': today_absent,
        'today_half_day': today_half_day,
        'total_marked_today': today_attendance.count(),
        'pending_today': active_teachers.count() - today_attendance.count(),
    }
    
    return render(request, 'attendance/dashboard.html', context)

@unauthenticated_user
def mark_attendance(request, teacher_id=None):
    """Mark attendance for single teacher"""
    today = timezone.now().date()
    
    if teacher_id is None and 'teacher' in request.GET:
        teacher_id = request.GET.get('teacher')

    if teacher_id:
        teacher = get_object_or_404(Teacher, pk=teacher_id, is_active=True)
        attendance, created = Attendance.objects.get_or_create(
            teacher=teacher,
            date=today,
            defaults={'status': 'present'}
        )
    else:
        teacher = None
        attendance = None
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            if not attendance.teacher_id:
                attendance.teacher_id = request.POST.get('teacher')
            attendance.marked_by = request.user.username if hasattr(request, 'user') else 'Admin'
            attendance.save()
            
            messages.success(request, f'Attendance marked for {attendance.teacher.full_name}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Attendance marked successfully'})
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance, initial={'date': today})
    
    active_teachers = Teacher.objects.filter(is_active=True, status='active')
    
    context = {
        'form': form,
        'teacher': teacher,
        'active_teachers': active_teachers,
        'today': today,
    }
    
    return render(request, 'attendance/mark_attendance.html', context)

@unauthenticated_user
def bulk_mark_attendance(request):
    """Mark attendance for multiple teachers at once"""
    today = timezone.now().date()
    
    today = timezone.now().date()
    
    if request.method == 'POST':
        selected_date_str = request.POST.get('attendance_date', str(today))
        # ✅ Convert to date object
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

        marked_count = 0
        active_teachers = Teacher.objects.filter(is_active=True)
        
        for teacher in active_teachers:
            status = request.POST.get(f'status_{teacher.id}')
            remarks = request.POST.get(f'remarks_{teacher.id}', '')
            
            if status:
                attendance, created = Attendance.objects.update_or_create(
                    teacher=teacher,
                    date=selected_date,  # ✅ Proper date object now
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user.username if hasattr(request, 'user') else 'Admin'
                    }
                )
                marked_count += 1
        
        messages.success(request, f'Attendance marked for {marked_count} staff members')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'marked_count': marked_count})
        return redirect('attendance_list')
    
    # Get active teachers and their today's attendance
    active_teachers = Teacher.objects.filter(is_active=True).order_by('full_name')
    
    # Get existing attendance for today
    existing_attendance = {}
    today_records = Attendance.objects.filter(date=today)
    for record in today_records:
        existing_attendance[record.teacher_id] = {
            'status': record.status,
            'remarks': record.remarks
        }
    
    # Prepare teachers with attendance data
    teachers_data = []
    for teacher in active_teachers:
        teacher_info = {
            'teacher': teacher,
            'existing_status': existing_attendance.get(teacher.id, {}).get('status', ''),
            'existing_remarks': existing_attendance.get(teacher.id, {}).get('remarks', ''),
        }
        teachers_data.append(teacher_info)
    
    context = {
        'teachers_data': teachers_data,
        'today': today,
        'status_choices': Attendance.STATUS_CHOICES,
    }
    
    return render(request, 'attendance/bulk_mark_attendance.html', context)

@unauthenticated_user
def attendance_list(request):
    """List all attendance records with filters"""
    # Get filter parameters
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    teacher_id = request.GET.get('teacher')
    status = request.GET.get('status')
    
    # Base queryset
    attendances = Attendance.objects.select_related('teacher').all()
    
    # Apply filters
    if month and year:
        attendances = attendances.filter(date__month=month, date__year=year)
    
    if teacher_id:
        attendances = attendances.filter(teacher_id=teacher_id)
    
    if status:
        attendances = attendances.filter(status=status)
    
    # Get all teachers for filter
    teachers = Teacher.objects.filter(is_active=True).order_by('full_name')
    
    # Prepare filter form
    filter_form = MonthlyAttendanceFilterForm(request.GET)
    
    context = {
        'attendances': attendances,
        'teachers': teachers,
        'filter_form': filter_form,
        'current_month': int(month),
        'current_year': int(year),
        'selected_teacher': teacher_id,
        'selected_status': status,
        'status_choices': Attendance.STATUS_CHOICES,
    }
    
    return render(request, 'attendance/attendance_list.html', context)

@unauthenticated_user
def teacher_attendance_detail(request, teacher_id):
    """View detailed attendance for a specific teacher"""
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    
    # Get month and year from request or use current
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    # Get attendance records
    attendances = Attendance.objects.filter(
        teacher=teacher,
        date__month=month,
        date__year=year
    ).order_by('date')
    
    # Calculate statistics
    total_days = monthrange(year, month)[1]
    sundays = sum(1 for day in range(1, total_days + 1) 
                 if datetime(year, month, day).weekday() == 6)
    working_days = total_days - sundays
    
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    half_day_count = attendances.filter(status='half_day').count()
    
    context = {
        'teacher': teacher,
        'attendances': attendances,
        'month': month,
        'year': year,
        'total_days': total_days,
        'working_days': working_days,
        'sundays': sundays,
        'present_count': present_count,
        'absent_count': absent_count,
        'half_day_count': half_day_count,
        'unmarked_days': working_days - attendances.count(),
    }
    
    return render(request, 'attendance/teacher_attendance_detail.html', context)


# ==================== SALARY VIEWS ====================
@unauthenticated_user
def salary_dashboard(request):
    """Salary management dashboard"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get current month salaries
    current_salaries = MonthlySalary.objects.filter(
        month=current_month,
        year=current_year
    ).select_related('teacher')
    
    # Statistics
    total_staff = Teacher.objects.filter(is_active=True).count()
    calculated_count = current_salaries.count()
    pending_count = total_staff - calculated_count
    
    paid_count = current_salaries.filter(payment_status='paid').count()
    total_payable = sum(s.net_salary for s in current_salaries)
    
    context = {
        'current_month': current_month,
        'current_year': current_year,
        'total_staff': total_staff,
        'calculated_count': calculated_count,
        'pending_count': pending_count,
        'paid_count': paid_count,
        'total_payable': total_payable,
        'recent_salaries': current_salaries[:10],
    }
    
    return render(request, 'salary/dashboard.html', context)

@unauthenticated_user
def calculate_monthly_salary(request):
    """Calculate salary for all staff for a given month"""
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        active_teachers = Teacher.objects.filter(is_active=True, status='active')
        calculated_count = 0
        
        for teacher in active_teachers:
            # Check if salary already calculated
            salary, created = MonthlySalary.objects.get_or_create(
                teacher=teacher,
                month=month,
                year=year
            )
            
            # Calculate salary based on attendance
            salary.calculate_salary()
            calculated_count += 1
        
        messages.success(request, f'Salary calculated for {calculated_count} staff members')
        return redirect('salary_list')
    
    # GET request - show form
    form = SalaryCalculationForm()
    context = {'form': form}
    
    return render(request, 'salary/calculate_salary.html', context)

@unauthenticated_user
def salary_list(request):
    """List all salary records"""
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    teacher_id = request.GET.get('teacher')
    payment_status = request.GET.get('payment_status')
    
    salaries = MonthlySalary.objects.select_related('teacher').filter(
        month=month,
        year=year
    )
    
    if teacher_id:
        salaries = salaries.filter(teacher_id=teacher_id)
    
    if payment_status:
        salaries = salaries.filter(payment_status=payment_status)
    
    teachers = Teacher.objects.filter(is_active=True).order_by('full_name')
    
    context = {
        'salaries': salaries,
        'teachers': teachers,
        'current_month': int(month),
        'current_year': int(year),
        'payment_status_choices': MonthlySalary.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'salary/salary_list.html', context)

@unauthenticated_user
def salary_detail(request, salary_id):
    """View detailed salary information"""
    salary = get_object_or_404(MonthlySalary, pk=salary_id)
    
    # Get attendance records for the month
    start_date = datetime(salary.year, salary.month, 1).date()
    end_date = datetime(salary.year, salary.month, 
                       monthrange(salary.year, salary.month)[1]).date()
    
    attendances = Attendance.objects.filter(
        teacher=salary.teacher,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    context = {
        'salary': salary,
        'attendances': attendances,
    }
    
    return render(request, 'salary/salary_detail.html', context)

@unauthenticated_user
def update_salary_payment(request, salary_id):
    """Update payment status for a salary record"""
    salary = get_object_or_404(MonthlySalary, pk=salary_id)
    if salary.payment_status == "paid":
        messages.info(request, 'Cannot edit the salary this salary is already paid..')
        return redirect('salary_detail', salary_id = salary_id )
    else:
        if request.method == 'POST':
            salary.payment_status = request.POST.get('payment_status')
            salary.payment_date = request.POST.get('payment_date')
            salary.payment_method = request.POST.get('payment_method')
            salary.payment_reference = request.POST.get('payment_reference')
            salary.save()
            if salary.payment_status == "paid":
                expense = Expense.objects.create(amount = salary.net_salary, perticulers = f'Salary Payment to {salary.teacher} of month {salary.month} by {salary.payment_method}', bill_number = salary.payment_reference  )
                expense.save()
            
            messages.success(request, 'Payment information updated successfully')
            return redirect('salary_detail', salary_id=salary_id)
    
        context = {'salary': salary}
        return render(request, 'salary/update_payment.html', context)

from decimal import Decimal

@unauthenticated_user
def make_deductions(request, salary_id):
    salary = get_object_or_404(MonthlySalary, id = salary_id)
    if salary.payment_status == "paid":
        messages.info(request, 'Cannot edit the salary this salary is already paid..')
        return redirect('salary_detail', salary_id = salary_id )
    else:
        if request.method == "POST":
            amount = request.POST['deduction_amount']
            remark = request.POST['deduction_remarks'] 
            salary.other_deductions = Decimal(str(amount))
            salary.other_deductions_remarks = remark
            salary.save()
            messages.success(request,"Deductions Added Success..")
            return redirect('salary_detail', salary_id = salary_id)
        else:
            return redirect('salary_detail', salary_id = salary_id)


@unauthenticated_user
def make_extra_payment(request, salary_id):
    salary = get_object_or_404(MonthlySalary, id = salary_id)
    if salary.payment_status == "paid":
        messages.info(request, 'Cannot edit the salary this salary is already paid..')
        return redirect('salary_detail', salary_id = salary_id )
    else:
        if request.method == "POST":
            amount = request.POST['extra_payment_amount']
            remark = request.POST['extra_payment_remarks'] 
            salary.other_additions = Decimal(str(amount))
            salary.other_additions_remarks = remark
            salary.save()
            messages.success(request,"Deductions Added Success..")
            return redirect('salary_detail', salary_id = salary_id)
        else:
            return redirect('salary_detail', salary_id = salary_id)