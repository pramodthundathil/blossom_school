from django import forms
from .models import Teacher
from datetime import date

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ['teacher_id', 'full_name', 'total_salary', 'created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter first name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter last name',
                'required': True
            }),
            'gender': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'max': date.today().isoformat()
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter nationality',
                'required': True
            }),
            'religion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter religion (optional)'
            }),
            'emirates_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '784-XXXX-XXXXXXX-X',
                'pattern': '[0-9]{3}-[0-9]{4}-[0-9]{7}-[0-9]{1}'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter passport number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+971 50 XXX XXXX',
                'required': True
            }),
            'alternative_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+971 XX XXX XXXX (optional)'
            }),
            'full_address': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Enter complete address',
                'rows': 3,
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter city',
                'required': True
            }),
            'po_box': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'PO Box (optional)'
            }),
            'position': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'reporting_to': forms.TextInput(attrs={
                'class': 'form-input',
                'value': 'Nursery Manager'
            }),
            'work_location': forms.TextInput(attrs={
                'class': 'form-input',
                'value': 'Blossom British Kids Center, Al Jurf, Ajman'
            }),
            'working_hours_start': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'value': '08:00'
            }),
            'working_hours_end': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'value': '17:00'
            }),
            'working_days': forms.TextInput(attrs={
                'class': 'form-input',
                'value': 'Monday to Saturday'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '1000.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'accommodation_allowance': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '700.00',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'transportation_allowance': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '500.00',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'probation_period_months': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'max': '12',
                'value': '6',
                'required': True
            }),
            'annual_leave_days': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'value': '30',
                'required': True
            }),
            'highest_qualification': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Bachelor in Early Childhood Education',
                'required': True
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'placeholder': 'Years of teaching experience',
                'required': True
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'List all relevant certifications (one per line)',
                'rows': 3
            }),
            'languages_spoken': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., English, Arabic, Hindi'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'cv_document': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.doc,.docx'
            }),
            'qualification_certificates': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'emirates_id_copy': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'passport_copy': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Emergency contact full name',
                'required': True
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Spouse, Parent, Sibling',
                'required': True
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+971 XX XXX XXXX',
                'required': True
            }),
            'reference_1_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Reference 1 name'
            }),
            'reference_1_contact': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Reference 1 contact (email or phone)'
            }),
            'reference_2_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Reference 2 name'
            }),
            'reference_2_contact': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Reference 2 contact (email or phone)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'offer_accepted': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'offer_acceptance_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'contract_signed': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'contract_signed_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Additional notes or comments',
                'rows': 4
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Teacher.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_emirates_id(self):
        emirates_id = self.cleaned_data.get('emirates_id')
        if emirates_id:
            # Remove dashes for validation
            clean_id = emirates_id.replace('-', '').replace(' ', '')
            if clean_id and len(clean_id) != 15:
                raise forms.ValidationError("Emirates ID must be 15 digits.")
            
            # Check uniqueness
            if emirates_id:
                qs = Teacher.objects.filter(emirates_id=emirates_id)
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise forms.ValidationError("This Emirates ID is already registered.")
        return emirates_id
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after start date.")
        
        # Validate working hours
        hours_start = cleaned_data.get('working_hours_start')
        hours_end = cleaned_data.get('working_hours_end')
        
        if hours_start and hours_end:
            if hours_end <= hours_start:
                raise forms.ValidationError("Working end time must be after start time.")
        
        return cleaned_data
    




from django import forms
from django.utils import timezone
from .models import Attendance, Teacher, MonthlySalary

class AttendanceForm(forms.ModelForm):
    """Form for marking single attendance"""
    
    class Meta:
        model = Attendance
        fields = ['teacher', 'date', 'status', 'remarks']
        widgets = {
            'teacher': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Add any remarks or reason for absence...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active teachers
        self.fields['teacher'].queryset = Teacher.objects.filter(
            is_active=True
        ).order_by('full_name')
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        teacher = cleaned_data.get('teacher')
        
        # Check for duplicate attendance
        if date and teacher:
            existing = Attendance.objects.filter(
                teacher=teacher,
                date=date
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Attendance already marked for {teacher.full_name} on {date}'
                )
        
        return cleaned_data


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking"""
    
    attendance_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'required': True
        }),
        initial=timezone.now().date(),
        label='Attendance Date'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MonthlyAttendanceFilterForm(forms.Form):
    """Form for filtering attendance records"""
    
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        initial=timezone.now().month,
        required=False
    )
    
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 2020,
            'max': 2050
        }),
        initial=timezone.now().year,
        required=False
    )
    
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True).order_by('full_name'),
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False,
        empty_label='All Teachers'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Attendance.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False
    )


class SalaryCalculationForm(forms.Form):
    """Form for calculating monthly salaries"""
    
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input', 'required': True}),
        initial=timezone.now().month,
        label='Select Month'
    )
    
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'min': 2020,
            'max': 2050,
            'required': True
        }),
        initial=timezone.now().year,
        label='Select Year'
    )
    
    recalculate = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label='Recalculate if already exists',
        help_text='Check this to recalculate salaries that have already been calculated'
    )


class SalaryPaymentUpdateForm(forms.ModelForm):
    """Form for updating salary payment information"""
    
    class Meta:
        model = MonthlySalary
        fields = ['payment_status', 'payment_date', 'payment_method', 'payment_reference', 'remarks']
        widgets = {
            'payment_status': forms.Select(attrs={'class': 'form-input'}),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'payment_method': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Bank Transfer, Cash, Cheque'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Transaction ID or reference number'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Any additional notes...'
            }),
        }