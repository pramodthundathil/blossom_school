from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from home.models import  FeeCategory
from students.models import Student

User =  get_user_model()
# New Payment Management Models

class FeeStructure(models.Model):
    """Define fee amounts for different categories and academic years"""
    FREQUENCY_CHOICES = [
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('one_time', 'One Time'),
    ]
    
    academic_year = models.IntegerField()
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    is_mandatory = models.BooleanField(default=True)
    late_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    due_date = models.IntegerField(default=10, help_text="Due date of each month (1-31)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['academic_year', 'fee_category']
        ordering = ['academic_year', 'fee_category__name']

    def __str__(self):
        return f"{self.fee_category.name} - {self.academic_year} - ${self.amount}"


class StudentFeeAssignment(models.Model):
    """Assign specific fees to students with custom amounts and discounts"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_assignments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    custom_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Leave blank to use default fee structure amount"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    final_amount  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,)
    class Meta:
        unique_together = ['student', 'fee_structure']
        ordering = ['student', 'fee_structure__fee_category__name']

    def get_final_amount(self):
        """Calculate final amount after discounts"""
        base_amount = self.custom_amount or self.fee_structure.amount
        
        # Apply percentage discount first
        amount_after_percentage = base_amount - (base_amount * self.discount_percentage / 100)
        
        # Apply fixed amount discount
        self.final_amount = final_amount = amount_after_percentage - self.discount_amount
        self.save()
        return max(final_amount, 0)  # Ensure amount is not negative

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.fee_structure.fee_category.name}"


class PaymentPlan(models.Model):
    """Define payment plans for students (monthly, quarterly, etc.)"""
    PLAN_TYPE_CHOICES = [
        ('full', 'Full Payment'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_plans')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    academic_year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.PositiveIntegerField(default=1)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    installment_frequency = models.PositiveIntegerField(default=30, help_text="Days between installments")
    start_date = models.DateField()
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'academic_year', 'fee_category']

    def save(self, *args, **kwargs):
        # Calculate balance amount
        self.balance_amount = self.total_amount - self.advance_amount
        # Calculate installment amount based on balance
        if self.number_of_installments > 0:
            self.installment_amount = self.balance_amount / self.number_of_installments
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.plan_type} - {self.academic_year}"


class PaymentInstallment(models.Model):
    """Individual installments for payment plans"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partially_paid', 'Partially Paid'),
    ]

    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)

    class Meta:
        unique_together = ['payment_plan', 'installment_number']
        ordering = ['payment_plan', 'installment_number']

    def get_outstanding_amount(self):
        return self.amount + self.late_fee - self.paid_amount

    def update_status(self):
        """Update status based on payment amount and due date"""
        if self.paid_amount >= self.amount + self.late_fee:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        elif timezone.now().date() > self.due_date:
            self.status = 'overdue'
            self.is_overdue = True
        else:
            self.status = 'pending'

    def __str__(self):
        return f"{self.payment_plan.student.get_full_name()} - Installment {self.installment_number}"

class Payment(models.Model):
    """Main payment transaction model"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    ]

    # Primary identification
    payment_id = models.CharField(max_length=50, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment method and status
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField()
    
    # Additional info
    remarks = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    
    # Administrative
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['student']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['payment_status']),
        ]

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        
        # Calculate net amount
        self.net_amount = self.total_amount - self.discount_amount + self.late_fee_amount
        
        super().save(*args, **kwargs)

    def generate_payment_id(self):
        """Generate unique payment ID"""
        import datetime
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        
        last_payment = Payment.objects.filter(
            payment_id__startswith=f'PAY{year}{month:02d}'
        ).order_by('-payment_id').first()
        
        if last_payment:
            last_number = int(last_payment.payment_id[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'PAY{year}{month:02d}{new_number:04d}'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.student.get_full_name()} - ${self.net_amount}"


class PaymentItem(models.Model):
    """Individual items/fees included in a payment"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_items')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    installment = models.ForeignKey(PaymentInstallment, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.net_amount = self.amount - self.discount_amount + self.late_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment.payment_id} - {self.fee_category.name} - ${self.net_amount}"


class PaymentReminder(models.Model):
    """Payment reminders for overdue fees"""
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('letter', 'Letter'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_reminders')
    installment = models.ForeignKey(PaymentInstallment, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.student.get_full_name()} - {self.reminder_type}"


class StudentLedger(models.Model):
    """Track all financial transactions for a student"""
    TRANSACTION_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ledger_entries')
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, null = True, blank=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.transaction_type} - ${self.amount}"