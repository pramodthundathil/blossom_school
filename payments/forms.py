from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import (
    Payment, PaymentItem, PaymentPlan, FeeStructure, 
    StudentFeeAssignment, FeeCategory, Student, PaymentInstallment
)


class PaymentForm(forms.ModelForm):
    """Main payment form"""
    class Meta:
        model = Payment
        fields = [
            'student', 'payment_method', 'payment_date', 
            'transaction_reference', 'remarks'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'transaction_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction/Reference Number'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional remarks or notes'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')


class PaymentItemForm(forms.ModelForm):
    """Form for individual payment items"""
    class Meta:
        model = PaymentItem
        fields = ['fee_category', 'description', 'amount', 'discount_amount', 'late_fee']
        widgets = {
            'fee_category': forms.Select(attrs={
                'class': 'form-control fee-category-select'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control amount-input',
                'step': '0.01',
                'min': '0'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control discount-input',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'late_fee': forms.NumberInput(attrs={
                'class': 'form-control late-fee-input',
                'step': '0.01',
                'min': '0',
                'value': '0'
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_discount_amount(self):
        discount = self.cleaned_data.get('discount_amount', 0)
        amount = self.cleaned_data.get('amount', 0)
        
        if discount > amount:
            raise forms.ValidationError("Discount cannot be greater than the amount.")
        return discount


# Create formset for multiple payment items
PaymentItemFormSet = inlineformset_factory(
    Payment, PaymentItem, 
    form=PaymentItemForm, 
    extra=1, 
    can_delete=True,
    min_num=1,
    validate_min=True
)


class PaymentPlanForm(forms.ModelForm):
    """Form for creating payment plans"""
    class Meta:
        model = PaymentPlan
        fields = [
            'student', 'plan_type', 'academic_year', 'total_amount',
            'number_of_installments', 'start_date'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'plan_type': forms.Select(attrs={
                'class': 'form-control plan-type-select'
            }),
            'academic_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'number_of_installments': forms.NumberInput(attrs={
                'class': 'form-control installments-input',
                'min': '1',
                'max': '12'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')
        if total_amount and total_amount <= 0:
            raise forms.ValidationError("Total amount must be greater than zero.")
        return total_amount

    def clean_number_of_installments(self):
        installments = self.cleaned_data.get('number_of_installments')
        plan_type = self.cleaned_data.get('plan_type')
        
        if plan_type == 'monthly' and installments > 12:
            raise forms.ValidationError("Monthly plans cannot have more than 12 installments.")
        elif plan_type == 'quarterly' and installments > 4:
            raise forms.ValidationError("Quarterly plans cannot have more than 4 installments.")
        
        return installments


class FeeStructureForm(forms.ModelForm):
    """Form for managing fee structures"""
    class Meta:
        model = FeeStructure
        fields = [
            'academic_year', 'fee_category', 'amount', 'frequency',
            'is_mandatory', 'late_fee_percentage', 'due_date', 'is_active'
        ]
        widgets = {
            'academic_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2030'
            }),
            'fee_category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'late_fee_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'due_date': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '31'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class StudentFeeAssignmentForm(forms.ModelForm):
    """Form for assigning fees to students"""
    class Meta:
        model = StudentFeeAssignment
        fields = [
            'student', 'fee_structure', 'custom_amount', 
            'discount_percentage', 'discount_amount', 'start_date', 'end_date'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'fee_structure': forms.Select(attrs={
                'class': 'form-control fee-structure-select'
            }),
            'custom_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Leave blank to use default amount'
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'value': '0'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data


class PaymentSearchForm(forms.Form):
    """Form for searching and filtering payments"""
    student_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by student name'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + list(Payment.PAYMENT_METHOD_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    payment_status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Payment.PAYMENT_STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class BulkReminderForm(forms.Form):
    """Form for sending bulk payment reminders"""
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('letter', 'Letter'),
    ]
    
    reminder_type = forms.ChoiceField(
        choices=REMINDER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Use {student_name}, {amount}, {due_date} for personalization'
        }),
        help_text="Available variables: {student_name}, {amount}, {due_date}"
    )


class DiscountForm(forms.Form):
    """Form for applying discounts"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    discount_type = forms.ChoiceField(
        choices=DISCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control discount-type-select'
        })
    )
    
    discount_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    
    reason = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reason for discount'
        })
    )

    def clean_discount_value(self):
        discount_value = self.cleaned_data.get('discount_value')
        discount_type = self.cleaned_data.get('discount_type')
        
        if discount_type == 'percentage' and discount_value > 100:
            raise forms.ValidationError("Percentage discount cannot be more than 100%.")
        
        if discount_value <= 0:
            raise forms.ValidationError("Discount value must be greater than zero.")
        
        return discount_value


class PaymentReportForm(forms.Form):
    """Form for generating payment reports"""
    REPORT_TYPE_CHOICES = [
        ('summary', 'Payment Summary'),
        ('detailed', 'Detailed Payments'),
        ('overdue', 'Overdue Payments'),
        ('defaulters', 'Defaulters Report'),
        ('collection', 'Collection Report'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class_room = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Classes",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    export_format = forms.ChoiceField(
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from .models import ClassRooms
        self.fields['class_room'].queryset = ClassRooms.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("From date must be before to date.")
        
        return cleaned_data


class QuickPaymentForm(forms.Form):
    """Simplified form for quick payments"""
    student = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={
            'class': 'form-control select2'
        })
    )
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional remarks'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')


class PaymentPlanEditForm(forms.ModelForm):
    """Form for editing existing payment plans"""
    class Meta:
        model = PaymentPlan
        fields = ['total_amount', 'installment_amount', 'status', 'is_active']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'installment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class PaymentInstallmentEditForm(forms.ModelForm):
    """Form for editing payment installments"""
    class Meta:
        model = PaymentInstallment
        fields = ['due_date', 'amount', 'late_fee', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class PaymentInstallmentAddForm(forms.ModelForm):
    """Form for adding a new payment installment"""
    class Meta:
        model = PaymentInstallment
        fields = ['due_date', 'amount', 'late_fee']
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': '0'}),
        }
