from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Teacher(models.Model):
    """Model for managing teachers and staff members"""
    
    # Position Choices
    POSITION_CHOICES = [
        ('nursery_teacher', 'Nursery Teacher'),
        ('assistant_teacher', 'Assistant Teacher'),
        ('head_teacher', 'Head Teacher'),
        ('manager', 'Manager'),
        ('admin_staff', 'Administrative Staff'),
        ('support_staff', 'Support Staff'),
    ]
    
    # Employment Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_probation', 'On Probation'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    # Personal Information
    teacher_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100)
    religion = models.CharField(max_length=100, blank=True)
    emirates_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    full_address = models.TextField()
    city = models.CharField(max_length=100)
    po_box = models.CharField(max_length=20, blank=True)
    
    # Employment Details
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reporting_to = models.CharField(max_length=100, default='Nursery Manager')
    work_location = models.CharField(max_length=200, default='Blossom British Kids Center, Al Jurf, Ajman')
    
    # Working Hours
    working_hours_start = models.TimeField(default='08:00')
    working_hours_end = models.TimeField(default='17:00')
    working_days = models.CharField(max_length=100, default='Monday to Saturday')
    
    # Salary Information
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    accommodation_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Employment Terms
    probation_period_months = models.IntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(12)])
    annual_leave_days = models.IntegerField(default=30)
    
    # Qualifications
    highest_qualification = models.CharField(max_length=200)
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)])
    certifications = models.TextField(blank=True, help_text="List all relevant certifications")
    languages_spoken = models.CharField(max_length=200, blank=True)
    
    # Documents
    photo = models.ImageField(upload_to='teacher_photos/', blank=True, null=True)
    cv_document = models.FileField(upload_to='teacher_documents/cv/', blank=True, null=True)
    qualification_certificates = models.FileField(upload_to='teacher_documents/certificates/', blank=True, null=True)
    emirates_id_copy = models.FileField(upload_to='teacher_documents/emirates_id/', blank=True, null=True)
    passport_copy = models.FileField(upload_to='teacher_documents/passport/', blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=20)
    
    # References
    reference_1_name = models.CharField(max_length=100, blank=True)
    reference_1_contact = models.CharField(max_length=100, blank=True)
    reference_2_name = models.CharField(max_length=100, blank=True)
    reference_2_contact = models.CharField(max_length=100, blank=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_probation')
    is_active = models.BooleanField(default=True)
    offer_accepted = models.BooleanField(default=True)
    offer_acceptance_date = models.DateField(null=True, blank=True)
    contract_signed = models.BooleanField(default=False)
    contract_signed_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher/Staff'
        verbose_name_plural = 'Teachers/Staff'
    
    def save(self, *args, **kwargs):
        # Generate teacher ID
        if not self.teacher_id:
            last_teacher = Teacher.objects.order_by('-id').first()
            if last_teacher and last_teacher.teacher_id:
                try:
                    last_num = int(last_teacher.teacher_id.split('-')[1])
                    new_num = last_num + 1
                except (IndexError, ValueError):
                    new_num = 1
            else:
                new_num = 1
            self.teacher_id = f'TCH-{new_num:05d}'
        
        # Calculate full name
        self.full_name = f"{self.first_name} {self.last_name}"
        
        # Calculate total salary
        self.total_salary = self.basic_salary + self.accommodation_allowance + self.transportation_allowance
        
        # Update status based on probation and dates
        if self.start_date:
            days_employed = (timezone.now().date() - self.start_date).days
            probation_days = self.probation_period_months * 30
            
            if days_employed < probation_days and self.status == 'on_probation':
                self.status = 'on_probation'
            elif days_employed >= probation_days and self.status == 'on_probation':
                self.status = 'active'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.teacher_id}) - {self.get_position_display()}"
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return None
    
    def get_years_employed(self):
        if self.start_date:
            delta = timezone.now().date() - self.start_date
            return round(delta.days / 365.25, 1)
        return 0
    
    def is_on_probation(self):
        if self.start_date:
            days_employed = (timezone.now().date() - self.start_date).days
            probation_days = self.probation_period_months * 30
            return days_employed < probation_days
        return True
    
    def probation_end_date(self):
        if self.start_date:
            from datetime import timedelta
            return self.start_date + timedelta(days=self.probation_period_months * 30)
        return None




from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from calendar import monthrange
from decimal import Decimal

class Attendance(models.Model):
    """Daily attendance tracking for teachers/staff"""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('sick_leave', 'Sick Leave'),
        ('half_day', 'Half Day'),
        ('sunday', 'Sunday (Weekly Off)'),
    ]
    
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, help_text="Reason for absence or any notes")
    
    # Metadata
    marked_by = models.CharField(max_length=100, blank=True)  # Admin who marked attendance
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['teacher', 'date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        indexes = [
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-mark Sunday as weekly off ONLY if no status is explicitly set
        # or if it's a new record without a status
        if self.date.weekday() == 6 and not self.status:  # Sunday = 6
            self.status = 'sunday'
        super().save(*args, **kwargs)


class MonthlySalary(models.Model):
    """Monthly salary calculation and payment tracking"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('hold', 'On Hold'),
    ]
    
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='monthly_salaries')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    
    # Salary Components
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    accommodation_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Attendance Details
    total_working_days = models.IntegerField(default=0)  # Excludes Sundays
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    half_days = models.IntegerField(default=0)
    sick_leave = models.IntegerField(default=0)
    # Additions
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                               help_text="Performance bonus or incentives")
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      help_text="Overtime payment")
    other_additions = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text="Any other additions")
    other_additions_remarks = models.CharField(max_length=200, blank=True,
                                              help_text="Remarks for other additions")
    total_additions = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    
    # Deductions
    absence_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                          help_text="Any other deductions")
    other_deductions_remarks = models.CharField(max_length=200, blank=True,
                                               help_text="Remarks for other deductions")
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Final Amount
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Payment Details
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, 
                                     help_text="e.g., Bank Transfer, Cash, Cheque")
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Notes
    remarks = models.TextField(blank=True)
    
    # Timestamps
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['teacher', 'month', 'year']
        verbose_name = 'Monthly Salary'
        verbose_name_plural = 'Monthly Salaries'
        indexes = [
            models.Index(fields=['teacher', 'month', 'year']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_month_name()} {self.year}"
    
    def get_month_name(self):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return months[self.month - 1]
    
    def calculate_salary(self):
        """Calculate salary based on attendance"""
        # Get salary components from teacher
        self.basic_salary = self.teacher.basic_salary
        self.accommodation_allowance = self.teacher.accommodation_allowance
        self.transportation_allowance = self.teacher.transportation_allowance
        self.gross_salary = self.basic_salary + self.accommodation_allowance + self.transportation_allowance
        
        # Get attendance records for the month
        from datetime import date
        start_date = date(self.year, self.month, 1)
        end_date = date(self.year, self.month, monthrange(self.year, self.month)[1])
        
        attendances = Attendance.objects.filter(
            teacher=self.teacher,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate working days (exclude Sundays)
        total_days = monthrange(self.year, self.month)[1]
        sundays = sum(1 for day in range(1, total_days + 1) 
                     if date(self.year, self.month, day).weekday() == 6)
        self.total_working_days = total_days - sundays
        
        # Count attendance
        self.days_present = attendances.filter(status='present').count()
        self.days_absent = attendances.filter(status='absent').count()
        self.half_days = attendances.filter(status='half_day').count()
        self.sick_leave = attendances.filter(status='sick_leave').count()
        
        # Calculate per day salary
        per_day_salary = self.gross_salary / Decimal(self.total_working_days)
        
        # Calculate deductions
        # Full day absent = full day deduction
        # Half day = 50% deduction
        # sick leave calculation is one sick leave is allowed in a month
        if self.sick_leave > 1:
            sick_leaves =  self.sick_leave - 1
        else:
            sick_leaves = 0
        absence_days = Decimal(self.days_absent) + (Decimal(self.half_days) * Decimal('0.5')) + Decimal(sick_leaves)
        self.absence_deduction = per_day_salary * absence_days
        
        # Total deductions
        self.total_deductions = self.absence_deduction + self.other_deductions
        
        # Net salary
        self.net_salary = self.gross_salary - self.total_deductions
        
        self.save()
    
    def save(self, *args, **kwargs):
        # Ensure all numeric fields have default values (not None)
        self.basic_salary = self.basic_salary or Decimal('0')
        self.accommodation_allowance = self.accommodation_allowance or Decimal('0')
        self.transportation_allowance = self.transportation_allowance or Decimal('0')
        self.bonus = self.bonus or Decimal('0')
        self.overtime_pay = self.overtime_pay or Decimal('0')
        self.other_additions = self.other_additions or Decimal('0')
        self.absence_deduction = self.absence_deduction or Decimal('0')
        self.other_deductions = self.other_deductions or Decimal('0')
        
        # Calculate totals
        self.gross_salary = self.basic_salary + self.accommodation_allowance + self.transportation_allowance
        self.total_additions = self.bonus + self.overtime_pay + self.other_additions
        self.total_deductions = self.absence_deduction + self.other_deductions
        self.net_salary = self.gross_salary + self.total_additions - self.total_deductions
        
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    """Leave request management (optional - for future use)"""
    
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sick Leave'),
        ('emergency', 'Emergency Leave'),
        ('personal', 'Personal Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval details
    approved_by = models.CharField(max_length=100, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def get_total_days(self):
        """Calculate total leave days excluding Sundays"""
        delta = self.end_date - self.start_date
        total_days = 0
        for i in range(delta.days + 1):
            day = self.start_date + timezone.timedelta(days=i)
            if day.weekday() != 6:  # Not Sunday
                total_days += 1
        return total_days