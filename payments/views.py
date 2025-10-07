from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum, Q, F
from decimal import Decimal
from datetime import datetime, timedelta
import json
from django.db import models
from home.decorators import unauthenticated_user

from Finance.models import Income, Expense
from .models import (
    Student, Payment, PaymentItem, FeeCategory, FeeStructure,
    StudentFeeAssignment, PaymentPlan, PaymentInstallment, StudentLedger, PaymentReminder
)
from .forms import PaymentForm, PaymentPlanForm  # You'll need to create these


class PaymentDashboardView(LoginRequiredMixin, ListView):
    """Dashboard showing payment overview"""
    template_name = 'payments/dashboard.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        return Payment.objects.select_related('student').order_by('-created_at')[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        context.update({
            'total_payments_today': Payment.objects.filter(
                payment_date=today,
                payment_status='completed'
            ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0,
            
            'total_payments_month': Payment.objects.filter(
                payment_date__month=current_month,
                payment_date__year=current_year,
                payment_status='completed'
            ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0,
            
            'pending_payments': PaymentInstallment.objects.filter(
                status__in=['pending', 'overdue']
            ).count(),
            
            'overdue_payments': PaymentInstallment.objects.filter(
                status='overdue'
            ).count(),
            
            'recent_payments': Payment.objects.select_related('student').filter(
                payment_status='completed'
            ).order_by('-created_at')[:5],
        })
        
        return context


# @unauthenticated_user
# def create_payment(request):
#     """Create a new payment with multiple fee categories"""
#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 # Get basic payment data
#                 student_id = request.POST.get('student_id')
#                 if not student_id:
#                     messages.error(request, 'Student selection is required.')
#                     return redirect('create_payment')
                
#                 student = get_object_or_404(Student, id=student_id)
                
#                 # Payment details
#                 payment_method = request.POST.get('payment_method')
#                 if not payment_method:
#                     messages.error(request, 'Payment method is required.')
#                     return redirect('create_payment')
                
#                 payment_date_str = request.POST.get('payment_date')
#                 if not payment_date_str:
#                     messages.error(request, 'Payment date is required.')
#                     return redirect('create_payment')
                
#                 try:
#                     payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
#                 except ValueError:
#                     messages.error(request, 'Invalid payment date format.')
#                     return redirect('create_payment')
                
#                 transaction_reference = request.POST.get('transaction_reference', '')
#                 remarks = request.POST.get('remarks', '')
                
#                 # Parse payment items - FIXED
#                 payment_items_json = request.POST.get('payment_items')
#                 if not payment_items_json:
#                     messages.error(request, 'No payment items found. Please add at least one payment item.')
#                     return redirect('create_payment')
                
#                 try:
#                     payment_items = json.loads(payment_items_json)
#                 except (json.JSONDecodeError, TypeError) as e:
#                     messages.error(request, f'Invalid payment items data: {str(e)}')
#                     return redirect('create_payment')
                
#                 if not payment_items or len(payment_items) == 0:
#                     messages.error(request, 'At least one payment item is required.')
#                     return redirect('create_payment')
                
#                 # Validate payment items
#                 valid_items = []
#                 for item in payment_items:
#                     try:
#                         fee_category_id = int(item.get('fee_category_id', 0))
#                         amount = float(item.get('amount', 0))
#                         discount = float(item.get('discount', 0))
#                         late_fee = float(item.get('late_fee', 0))
                        
#                         if fee_category_id <= 0:
#                             continue
#                         if amount <= 0:
#                             continue
                            
#                         # Verify fee category exists
#                         try:
#                             fee_category = FeeCategory.objects.get(id=fee_category_id)
#                         except FeeCategory.DoesNotExist:
#                             messages.error(request, f'Invalid fee category ID: {fee_category_id}')
#                             return redirect('create_payment')
                        
#                         valid_items.append({
#                             'fee_category_id': fee_category_id,
#                             'fee_category': fee_category,
#                             'amount': Decimal(str(amount)),
#                             'discount': Decimal(str(discount)),
#                             'late_fee': Decimal(str(late_fee)),
#                             'description': item.get('description', fee_category.name)
#                         })
                        
#                     except (ValueError, TypeError) as e:
#                         messages.error(request, f'Invalid payment item data: {str(e)}')
#                         return redirect('create_payment')
                
#                 if not valid_items:
#                     messages.error(request, 'No valid payment items found.')
#                     return redirect('create_payment')
                
#                 # Calculate totals
#                 total_amount = sum(item['amount'] for item in valid_items)
#                 total_discount = sum(item['discount'] for item in valid_items)
#                 total_late_fee = sum(item['late_fee'] for item in valid_items)
#                 net_amount = total_amount - total_discount + total_late_fee
                
#                 if net_amount <= 0:
#                     messages.error(request, 'Net payment amount must be greater than zero.')
#                     return redirect('create_payment')
                
#                 # Create payment record
#                 payment = Payment.objects.create(
#                     student=student,
#                     total_amount=total_amount,
#                     discount_amount=total_discount,
#                     late_fee_amount=total_late_fee,
#                     net_amount=net_amount,  # Add this field if it exists
#                     payment_method=payment_method,
#                     payment_date=payment_date,
#                     transaction_reference=transaction_reference,
#                     remarks=remarks,
#                     payment_status='completed',
#                     collected_by=request.user,
#                     created_at=timezone.now(),
#                     updated_at=timezone.now()
#                 )
                
#                 # Create payment items
#                 for item in valid_items:
#                     PaymentItem.objects.create(
#                         payment=payment,
#                         fee_category=item['fee_category'],
#                         description=item['description'],
#                         amount=item['amount'],
#                         discount_amount=item['discount'],
#                         late_fee=item['late_fee'],
#                         net_amount=item['amount'] - item['discount'] + item['late_fee']
#                     )
                    
#                     # Create ledger entry for each item
#                     net_item_amount = item['amount'] - item['discount'] + item['late_fee']
#                     StudentLedger.objects.create(
#                         student=student,
#                         transaction_date=payment_date,
#                         transaction_type='credit',
#                         fee_category=item['fee_category'],
#                         payment=payment,
#                         amount=net_item_amount,
#                         description=f"Payment - {item['description']}",
#                         reference_number=payment.payment_id
#                     )
                
#                 # Update any related installments if applicable
#                 for item in payment_items:
#                     if 'installment_id' in item and item['installment_id']:
#                         try:
#                             installment = PaymentInstallment.objects.get(id=item['installment_id'])
#                             installment.paid_amount += Decimal(str(item['amount']))
#                             installment.paid_date = payment_date
#                             installment.update_status()
#                             installment.save()
#                         except PaymentInstallment.DoesNotExist:
#                             pass  # Installment doesn't exist, skip
                
#                 messages.success(request, 
#                     f'Payment {payment.payment_id} created successfully! '
#                     f'Total amount: ${net_amount:.2f}')
                
#                 return redirect('payment_receipt', payment_id=payment.id)
                
#         except Exception as e:
#             # Log the full error for debugging
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.error(f'Payment creation error: {str(e)}', exc_info=True)
            
#             messages.error(request, f'Error creating payment: {str(e)}')
#             return redirect('create_payment')
    
#     # GET request - show the form
#     context = {
#         'students': Student.objects.filter(is_active=True).order_by('first_name', 'last_name'),
#         'fee_categories': FeeCategory.objects.all().order_by('name'),
#         'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
#         'today': timezone.now().date(),
#     }
    
#     return render(request, 'payments/create_payment.html', context)


@unauthenticated_user
def create_payment(request):
    """Create a new payment with multiple fee categories"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get basic payment data
                student_id = request.POST.get('student_id')
                if not student_id:
                    messages.error(request, 'Student selection is required.')
                    return redirect('create_payment')
                
                student = get_object_or_404(Student, id=student_id)
                
                # Payment details
                payment_method = request.POST.get('payment_method')
                if not payment_method:
                    messages.error(request, 'Payment method is required.')
                    return redirect('create_payment')
                
                payment_date_str = request.POST.get('payment_date')
                if not payment_date_str:
                    messages.error(request, 'Payment date is required.')
                    return redirect('create_payment')
                
                try:
                    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Invalid payment date format.')
                    return redirect('create_payment')
                
                transaction_reference = request.POST.get('transaction_reference', '')
                remarks = request.POST.get('remarks', '')
                
                # Parse payment items
                payment_items_json = request.POST.get('payment_items')
                if not payment_items_json:
                    messages.error(request, 'No payment items found. Please add at least one payment item.')
                    return redirect('create_payment')
                
                try:
                    payment_items = json.loads(payment_items_json)
                except (json.JSONDecodeError, TypeError) as e:
                    messages.error(request, f'Invalid payment items data: {str(e)}')
                    return redirect('create_payment')
                
                if not payment_items or len(payment_items) == 0:
                    messages.error(request, 'At least one payment item is required.')
                    return redirect('create_payment')
                
                # Validate payment items
                valid_items = []
                for item in payment_items:
                    try:
                        fee_category_id = int(item.get('fee_category_id', 0))
                        amount = float(item.get('amount', 0))
                        discount = float(item.get('discount', 0))
                        late_fee = float(item.get('late_fee', 0))
                        
                        if fee_category_id <= 0:
                            continue
                        if amount <= 0:
                            continue
                            
                        # Verify fee category exists
                        try:
                            fee_category = FeeCategory.objects.get(id=fee_category_id)
                        except FeeCategory.DoesNotExist:
                            messages.error(request, f'Invalid fee category ID: {fee_category_id}')
                            return redirect('create_payment')
                        
                        valid_items.append({
                            'fee_category_id': fee_category_id,
                            'fee_category': fee_category,
                            'amount': Decimal(str(amount)),
                            'discount': Decimal(str(discount)),
                            'late_fee': Decimal(str(late_fee)),
                            'description': item.get('description', fee_category.name),
                            'installment_id': item.get('installment_id')  # Capture installment ID
                        })
                        
                    except (ValueError, TypeError) as e:
                        messages.error(request, f'Invalid payment item data: {str(e)}')
                        return redirect('create_payment')
                
                if not valid_items:
                    messages.error(request, 'No valid payment items found.')
                    return redirect('create_payment')
                
                # Calculate totals
                total_amount = sum(item['amount'] for item in valid_items)
                total_discount = sum(item['discount'] for item in valid_items)
                total_late_fee = sum(item['late_fee'] for item in valid_items)
                net_amount = total_amount - total_discount + total_late_fee
                
                if net_amount <= 0:
                    messages.error(request, 'Net payment amount must be greater than zero.')
                    return redirect('create_payment')
                
                # Create payment record
                payment = Payment.objects.create(
                    student=student,
                    total_amount=total_amount,
                    discount_amount=total_discount,
                    late_fee_amount=total_late_fee,
                    net_amount=net_amount,
                    payment_method=payment_method,
                    payment_date=payment_date,
                    transaction_reference=transaction_reference,
                    remarks=remarks,
                    payment_status='completed',
                    collected_by=request.user,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                
                #income saving to db
                income = Income.objects.create(perticulers = f"Fee payment of  {str(student.get_full_name())} against {remarks} by {payment_method}", amount = net_amount,bill_number = payment.payment_id  )
                income.save()

                
                # Create payment items and update installments
                for item in valid_items:
                    PaymentItem.objects.create(
                        payment=payment,
                        fee_category=item['fee_category'],
                        description=item['description'],
                        amount=item['amount'],
                        discount_amount=item['discount'],
                        late_fee=item['late_fee'],
                        net_amount=item['amount'] - item['discount'] + item['late_fee']
                    )
                    
                    # Create ledger entry for each item
                    net_item_amount = item['amount'] - item['discount'] + item['late_fee']
                    StudentLedger.objects.create(
                        student=student,
                        transaction_date=payment_date,
                        transaction_type='credit',
                        fee_category=item['fee_category'],
                        payment=payment,
                        amount=net_item_amount,
                        description=f"Payment - {item['description']}",
                        reference_number=payment.payment_id
                    )
                    
                    # Update related installment if exists
                    if item.get('installment_id'):
                        try:
                            installment = PaymentInstallment.objects.get(id=item['installment_id'])
                            installment.paid_amount += item['amount']
                            installment.paid_date = payment_date
                            installment.update_status()
                            installment.save()
                        except PaymentInstallment.DoesNotExist:
                            pass
                
                messages.success(request, 
                    f'Payment {payment.payment_id} created successfully! '
                    f'Total amount: ${net_amount:.2f}')
                
                return redirect('payment_receipt', payment_id=payment.id)
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Payment creation error: {str(e)}', exc_info=True)
            
            messages.error(request, f'Error creating payment: {str(e)}')
            return redirect('create_payment')
    
    # GET request - show the form
    context = {
        'students': Student.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'fee_categories': FeeCategory.objects.all().order_by('name'),
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'today': timezone.now().date(),
    }
    
    # Check if we're pre-populating from an installment
    student_id = request.GET.get('student_id')
    installment_id = request.GET.get('installment_id')
    
    if student_id and installment_id:
        try:
            student = Student.objects.get(id=student_id)
            installment = PaymentInstallment.objects.get(id=installment_id)
            
            # Add pre-population data to context
            context['prepopulated'] = {
                'student': student,
                'installment': installment,
                'fee_category': installment.payment_plan.fee_structure.fee_category if hasattr(installment.payment_plan, 'fee_structure') else None,
                'amount': float(installment.get_outstanding_amount()),
                'late_fee': float(installment.late_fee),
                'description': f"{installment.payment_plan.plan_type.title()} - Installment {installment.installment_number}"
            }
        except (Student.DoesNotExist, PaymentInstallment.DoesNotExist):
            messages.warning(request, 'Invalid student or installment.')
    
    return render(request, 'payments/create_payment.html', context)

# Additional helper view for outstanding fees AJAX
@unauthenticated_user
def get_student_outstanding_fees(request, student_id):
    """Get outstanding fees for a specific student via AJAX"""
    try:
        student = get_object_or_404(Student, id=student_id)
        
        # Get outstanding fees - this depends on your fee structure
        # Adjust the query based on your actual models
        outstanding_fees = []
        
        # Example query - modify based on your actual fee tracking system
        from django.db.models import Q, Sum
        
        # Get unpaid or partially paid fees
        unpaid_fees = StudentLedger.objects.filter(
            student=student,
            transaction_type='debit'  # Assuming debit means fees owed
        ).exclude(
            fee_category__in=StudentLedger.objects.filter(
                student=student,
                transaction_type='credit',  # Payments
                fee_category__isnull=False
            ).values('fee_category')
        ).values('fee_category', 'fee_category__name').annotate(
            total_amount=Sum('amount')
        )
        
        for fee in unpaid_fees:
            # Check if this fee is overdue (you'll need to implement this logic)
            is_overdue = False  # Implement your overdue logic here
            late_fee = 0  # Calculate late fee if applicable
            
            outstanding_fees.append({
                'fee_category_id': fee['fee_category'],
                'fee_category': fee['fee_category__name'],
                'amount': float(fee['total_amount']),
                'late_fee': late_fee,
                'is_overdue': is_overdue
            })
        
        return JsonResponse({
            'success': True,
            'outstanding_fees': outstanding_fees,
            'total_outstanding': sum(fee['amount'] for fee in outstanding_fees)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    

@unauthenticated_user
def payment_receipt(request, payment_id):
    """Generate payment receipt"""
    payment = get_object_or_404(
        Payment.objects.select_related('student').prefetch_related('payment_items__fee_category'),
        id=payment_id
    )
    
    context = {
        'payment': payment,
        'school_name': 'Blossom British School',  # Configure this
        'school_address': 'Ajman UAE',  # Configure this
    }
    
    return render(request, 'payments/receipt.html', context)


class PaymentListView(LoginRequiredMixin, ListView):
    """List all payments with filtering options"""
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('student', 'collected_by').order_by('-created_at')
        
        # Apply filters
        student_name = self.request.GET.get('student_name')
        if student_name:
            queryset = queryset.filter(
                Q(student__first_name__icontains=student_name) |
                Q(student__last_name__icontains=student_name)
            )
        
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(payment_status=status)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(payment_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(payment_date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
            'payment_statuses': Payment.PAYMENT_STATUS_CHOICES,
        })
        return context


@unauthenticated_user
def create_payment_plan(request, student_id):
    """Create payment plan for a student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                plan_type = request.POST.get('plan_type')
                academic_year = int(request.POST.get('academic_year'))
                total_amount = Decimal(request.POST.get('total_amount'))
                number_of_installments = int(request.POST.get('number_of_installments', 1))
                start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
                
                # Calculate installment amount
                installment_amount = total_amount / number_of_installments
                
                # Create payment plan
                payment_plan = PaymentPlan.objects.create(
                    student=student,
                    plan_type=plan_type,
                    academic_year=academic_year,
                    total_amount=total_amount,
                    number_of_installments=number_of_installments,
                    installment_amount=installment_amount,
                    start_date=start_date,
                    created_by=request.user
                )
                
                # Create installments
                current_date = start_date
                for i in range(number_of_installments):
                    # Calculate due date based on plan type
                    if plan_type == 'monthly':
                        due_date = current_date.replace(day=10)  # 10th of each month
                        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                    elif plan_type == 'quarterly':
                        due_date = current_date
                        current_date += timedelta(days=90)
                    else:
                        due_date = current_date + timedelta(days=30 * i)
                    
                    PaymentInstallment.objects.create(
                        payment_plan=payment_plan,
                        installment_number=i + 1,
                        due_date=due_date,
                        amount=installment_amount
                    )
                
                messages.success(request, f'Payment plan created successfully!')
                return redirect('student_payment_details', student_id=student.id)
                
        except Exception as e:
            messages.error(request, f'Error creating payment plan: {str(e)}')
    
    # Get student's fee assignments for calculation
    fee_assignments = StudentFeeAssignment.objects.filter(
        student=student,
        is_active=True
    ).select_related('fee_structure__fee_category')
    
    total_annual_fees = sum(assignment.get_final_amount() for assignment in fee_assignments)
    
    context = {
        'student': student,
        'fee_assignments': fee_assignments,
        'total_annual_fees': total_annual_fees,
        'plan_types': PaymentPlan.PLAN_TYPE_CHOICES,
    }
    
    return render(request, 'payments/create_payment_plan.html', context)


@unauthenticated_user
def student_payment_details(request, student_id):
    """Show detailed payment information for a student"""
    student = get_object_or_404(Student, id=student_id)
    
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
    }
    
    return render(request, 'payments/student_payment_details.html', context)


@unauthenticated_user
def overdue_payments_report(request):
    """Generate overdue payments report"""
    overdue_installments = PaymentInstallment.objects.filter(
        status='overdue'
    ).select_related('payment_plan__student').order_by('due_date')
    
    # Calculate late fees and update status
    for installment in overdue_installments:
        if installment.late_fee == 0:  # Calculate late fee if not already calculated
            days_overdue = (timezone.now().date() - installment.due_date).days
            if days_overdue > 0:
                # Get late fee percentage from fee structure
                fee_assignment = installment.payment_plan.student.fee_assignments.first()
                if fee_assignment:
                    late_fee_percentage = fee_assignment.fee_structure.late_fee_percentage
                    installment.late_fee = installment.amount * (late_fee_percentage / 100)
                    installment.save()
    
    context = {
        'overdue_installments': overdue_installments,
        'total_overdue_amount': sum(inst.get_outstanding_amount() for inst in overdue_installments),
    }
    
    return render(request, 'payments/overdue_report.html', context)


@unauthenticated_user
def payment_summary_report(request):
    """Generate payment summary report"""
    # Date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    payments = Payment.objects.filter(payment_status='completed')
    
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    # Summary statistics
    total_payments = payments.count()
    total_amount = payments.aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    total_discount = payments.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
    total_late_fees = payments.aggregate(Sum('late_fee_amount'))['late_fee_amount__sum'] or 0
    
    # Payment method breakdown
    payment_method_summary = payments.values('payment_method').annotate(
        count=models.Count('id'),
        total=Sum('net_amount')
    ).order_by('payment_method')
    
    # Daily collection summary
    daily_summary = payments.values('payment_date').annotate(
        count=models.Count('id'),
        total=Sum('net_amount')
    ).order_by('-payment_date')[:30]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_payments': total_payments,
        'total_amount': total_amount,
        'total_discount': total_discount,
        'total_late_fees': total_late_fees,
        'payment_method_summary': payment_method_summary,
        'daily_summary': daily_summary,
    }
    
    return render(request, 'payments/payment_summary_report.html', context)


@unauthenticated_user
def defaulter_report(request):
    """Generate defaulter report"""
    # Get students with overdue payments
    overdue_students = Student.objects.filter(
        payment_plans__installments__status='overdue'
    ).distinct().annotate(
        overdue_amount=Sum(
            F('payment_plans__installments__amount') + 
            F('payment_plans__installments__late_fee') - 
            F('payment_plans__installments__paid_amount'),
            filter=Q(payment_plans__installments__status='overdue')
        ),
        overdue_count=models.Count(
            'payment_plans__installments',
            filter=Q(payment_plans__installments__status='overdue')
        )
    ).order_by('-overdue_amount')
    
    context = {
        'defaulter_students': overdue_students,
        'total_defaulters': overdue_students.count(),
        'total_overdue_amount': sum(s.overdue_amount or 0 for s in overdue_students),
    }
    
    return render(request, 'payments/defaulter_report.html', context)


@unauthenticated_user
def export_payment_data(request):
    """Export payment data to Excel"""
    import xlsxwriter
    from django.http import HttpResponse
    from io import BytesIO
    
    # Create workbook
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Payment summary worksheet
    worksheet1 = workbook.add_worksheet('Payment Summary')
    
    # Headers
    headers = [
        'Payment ID', 'Student Name', 'Student ID', 'Payment Date',
        'Payment Method', 'Total Amount', 'Discount', 'Late Fee',
        'Net Amount', 'Status', 'Collected By'
    ]
    
    # Write headers
    for col, header in enumerate(headers):
        worksheet1.write(0, col, header)
    
    # Get payment data
    payments = Payment.objects.select_related('student', 'collected_by').order_by('-payment_date')
    
    # Write data
    for row, payment in enumerate(payments, 1):
        worksheet1.write(row, 0, payment.payment_id)
        worksheet1.write(row, 1, payment.student.get_full_name())
        worksheet1.write(row, 2, payment.student.student_id)
        worksheet1.write(row, 3, payment.payment_date.strftime('%Y-%m-%d'))
        worksheet1.write(row, 4, payment.get_payment_method_display())
        worksheet1.write(row, 5, float(payment.total_amount))
        worksheet1.write(row, 6, float(payment.discount_amount))
        worksheet1.write(row, 7, float(payment.late_fee_amount))
        worksheet1.write(row, 8, float(payment.net_amount))
        worksheet1.write(row, 9, payment.get_payment_status_display())
        worksheet1.write(row, 10, payment.collected_by.get_full_name() if payment.collected_by else '')
    
    # Overdue payments worksheet
    worksheet2 = workbook.add_worksheet('Overdue Payments')
    
    overdue_headers = [
        'Student Name', 'Student ID', 'Installment Number', 'Due Date',
        'Amount', 'Paid Amount', 'Outstanding', 'Days Overdue', 'Late Fee'
    ]
    
    for col, header in enumerate(overdue_headers):
        worksheet2.write(0, col, header)
    
    overdue_installments = PaymentInstallment.objects.filter(
        status='overdue'
    ).select_related('payment_plan__student').order_by('due_date')
    
    for row, installment in enumerate(overdue_installments, 1):
        days_overdue = (timezone.now().date() - installment.due_date).days
        worksheet2.write(row, 0, installment.payment_plan.student.get_full_name())
        worksheet2.write(row, 1, installment.payment_plan.student.student_id)
        worksheet2.write(row, 2, installment.installment_number)
        worksheet2.write(row, 3, installment.due_date.strftime('%Y-%m-%d'))
        worksheet2.write(row, 4, float(installment.amount))
        worksheet2.write(row, 5, float(installment.paid_amount))
        worksheet2.write(row, 6, float(installment.get_outstanding_amount()))
        worksheet2.write(row, 7, days_overdue)
        worksheet2.write(row, 8, float(installment.late_fee))
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=payment_report_{timezone.now().date()}.xlsx'
    
    return response


# Utility functions
@unauthenticated_user
def calculate_student_balance(student):
    """Calculate current balance for a student"""
    # Get all completed payments
    total_paid = Payment.objects.filter(
        student=student,
        payment_status='completed'
    ).aggregate(Sum('net_amount'))['net_amount__sum'] or 0
    
    # Get total outstanding installments
    total_outstanding = PaymentInstallment.objects.filter(
        payment_plan__student=student,
        status__in=['pending', 'overdue', 'partially_paid']
    ).aggregate(
        total=Sum(
            F('amount') + F('late_fee') - F('paid_amount')
        )
    )['total'] or 0
    
    return {
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'balance': total_outstanding - total_paid
    }

@unauthenticated_user
def update_overdue_installments():
    """Update overdue installments and calculate late fees"""
    today = timezone.now().date()
    
    # Get pending installments that are past due date
    pending_installments = PaymentInstallment.objects.filter(
        due_date__lt=today,
        status='pending'
    )
    
    for installment in pending_installments:
        installment.status = 'overdue'
        installment.is_overdue = True
        
        # Calculate late fee if not already calculated
        if installment.late_fee == 0:
            fee_assignment = installment.payment_plan.student.fee_assignments.first()
            if fee_assignment:
                late_fee_percentage = fee_assignment.fee_structure.late_fee_percentage
                installment.late_fee = installment.amount * (late_fee_percentage / 100)
        
        installment.save()


@unauthenticated_user
def bulk_payment_reminder(request):
    """Send bulk payment reminders"""
    if request.method == 'POST':
        reminder_type = request.POST.get('reminder_type')
        message_template = request.POST.get('message')
        
        # Get overdue installments
        overdue_installments = PaymentInstallment.objects.filter(
            status='overdue'
        ).select_related('payment_plan__student')
        
        reminders_created = 0
        for installment in overdue_installments:
            # Customize message for each student
            personalized_message = message_template.format(
                student_name=installment.payment_plan.student.get_full_name(),
                amount=installment.get_outstanding_amount(),
                due_date=installment.due_date
            )
            
            PaymentReminder.objects.create(
                student=installment.payment_plan.student,
                installment=installment,
                reminder_type=reminder_type,
                scheduled_date=timezone.now(),
                message=personalized_message,
                created_by=request.user
            )
            reminders_created += 1
        
        messages.success(request, f'{reminders_created} payment reminders created successfully!')
        return redirect('payment_dashboard')
    
    return render(request, 'payments/bulk_reminder.html')


# AJAX endpoints

@unauthenticated_user
def get_fee_structure_amount(request):
    """Get fee structure amount for a category and year"""
    fee_category_id = request.GET.get('fee_category_id')
    academic_year = request.GET.get('academic_year')
    
    try:
        fee_structure = FeeStructure.objects.get(
            fee_category_id=fee_category_id,
            academic_year=academic_year,
            is_active=True
        )
        return JsonResponse({
            'amount': float(fee_structure.amount),
            'frequency': fee_structure.frequency,
            'late_fee_percentage': float(fee_structure.late_fee_percentage)
        })
    except FeeStructure.DoesNotExist:
        return JsonResponse({'error': 'Fee structure not found'}, status=404)


@unauthenticated_user
def validate_payment_amount(request):
    """Validate payment amount against outstanding balance"""
    student_id = request.GET.get('student_id')
    payment_amount = Decimal(request.GET.get('amount', '0'))
    
    student = get_object_or_404(Student, id=student_id)
    balance_info = calculate_student_balance(student)
    
    if payment_amount > balance_info['total_outstanding']:
        return JsonResponse({
            'valid': False,
            'message': f'Payment amount exceeds outstanding balance of ${balance_info["total_outstanding"]}'
        })
    
    return JsonResponse({'valid': True})

@unauthenticated_user
def mark_as_paid(request, pk):
    installment = get_object_or_404( PaymentInstallment, id= pk )
    installment.paid_amount = installment.amount
    installment.status = 'paid'
    installment.save()
    messages.success(request, 'Installment marked as Paid')
    return redirect("student_payment_details", installment.payment_plan.student.id)