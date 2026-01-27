from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum, Q, F
from decimal import Decimal
from datetime import datetime, timedelta
import json
from django.db import models
from home.decorators import unauthenticated_user, user_controls
from django.utils.decorators import method_decorator
from Finance.models import Income, Expense
from .models import (
    Student, Payment, PaymentItem, FeeCategory, FeeStructure,
    StudentFeeAssignment, PaymentPlan, PaymentInstallment, StudentLedger, PaymentReminder
)
from .forms import PaymentForm, PaymentPlanForm, PaymentPlanEditForm, PaymentInstallmentEditForm, PaymentInstallmentAddForm

# @method_decorator(user_controls, name='dispatch')
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
            
            'pending_installments_this_month': PaymentInstallment.objects.select_related('payment_plan__student').filter(
                status__in=['pending', 'overdue', 'partially_paid'],
                due_date__month=current_month,
                due_date__year=current_year
            ).order_by('due_date'),

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
                income = Income.objects.create(perticulers = f"Fee payment of  {str(student.get_full_name())} against {remarks} by {payment_method}", amount = net_amount,bill_number = payment.payment_id ,date = payment_date )
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


class PendingInstallmentListView(LoginRequiredMixin, ListView):
    """List pending and overdue installments"""
    model = PaymentInstallment
    template_name = 'payments/pending_installments_list.html'
    context_object_name = 'installments'
    paginate_by = 50

    def get_queryset(self):
        queryset = PaymentInstallment.objects.select_related('payment_plan__student').filter(
            status__in=['pending', 'overdue', 'partially_paid']
        ).order_by('due_date')

        # Filter mode
        mode = self.request.GET.get('mode')
        
        if mode == 'this_month':
            today = timezone.now().date()
            queryset = queryset.filter(
                due_date__month=today.month,
                due_date__year=today.year
            )
        
        # Date range filters (override mode if present)
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(due_date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
             queryset = queryset.filter(due_date__lte=date_to)

        # Student search
        search = self.request.GET.get('search')
        if search:
             queryset = queryset.filter(
                Q(payment_plan__student__first_name__icontains=search) |
                Q(payment_plan__student__last_name__icontains=search) |
                Q(payment_plan__student__student_id__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = self.request.GET.get('mode', 'all')
        
        # Add overdue calculation
        for installment in context['installments']:
             if installment.status == 'overdue' or (installment.status == 'pending' and installment.due_date < timezone.now().date()):
                installment.days_overdue = (timezone.now().date() - installment.due_date).days
                installment.is_overdue = True
             else:
                installment.is_overdue = False
                
        return context


from django.http import JsonResponse
from django.urls import reverse

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
                advance_amount = Decimal(request.POST.get('advance_amount', '0'))
                number_of_installments = int(request.POST.get('number_of_installments', 1))
                installment_frequency = int(request.POST.get('installment_frequency', 30))
                start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
                fee_category_id = request.POST.get('fee_category')
                
                # Validate advance amount
                if advance_amount > total_amount:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': 'Advance amount cannot exceed total amount'
                        })
                    messages.error(request, 'Advance amount cannot exceed total amount')
                    return redirect('create_payment_plan', student_id=student_id)
                
                # Get fee category
                fee_category = None
                if fee_category_id:
                    fee_category = FeeCategory.objects.get(id=fee_category_id)
                
                # Calculate balance and installment amount
                balance_amount = total_amount - advance_amount
                installment_amount = balance_amount / number_of_installments if number_of_installments > 0 else balance_amount
                
                # Custom Installments Logic
                if plan_type == 'custom':
                    custom_installments_json = request.POST.get('custom_installments')
                    if not custom_installments_json:
                        raise ValueError("Custom installments are required for custom plan type")
                    
                    try:
                        custom_installments = json.loads(custom_installments_json)
                    except json.JSONDecodeError:
                         raise ValueError("Invalid custom installments data")
                         
                    if not custom_installments:
                         raise ValueError("At least one installment is required")
                         
                    # Verify total amount matches
                    installments_total = sum(Decimal(str(inst['amount'])) for inst in custom_installments)
                    if abs(installments_total - balance_amount) > Decimal('0.01'):
                         raise ValueError(f"Sum of installments ({installments_total}) must match balance amount ({balance_amount})")
                         
                    number_of_installments = len(custom_installments)
                    installment_amount = 0 # Variable for plan model, though individual installments differ
                    installment_frequency = 0 # Not applicable for custom

                # Create payment plan
                session_type = request.POST.get('session_type', 'morning')
                registration_fee_included = request.POST.get('registration_fee_included') == 'on'
                
                payment_plan = PaymentPlan.objects.create(
                    student=student,
                    plan_type=plan_type,
                    academic_year=academic_year,
                    total_amount=total_amount,
                    advance_amount=advance_amount,
                    balance_amount=balance_amount,
                    number_of_installments=number_of_installments,
                    installment_amount=installment_amount,
                    installment_frequency=installment_frequency,
                    start_date=start_date,
                    fee_category=fee_category,
                    session_type=session_type,
                    registration_fee_included=registration_fee_included,
                    status='active',
                    created_by=request.user
                )
                
                # Handle Registration Fee
                if registration_fee_included:
                    reg_fee_amount = Decimal(request.POST.get('registration_fee_amount', '0'))
                    if reg_fee_amount > 0:
                        reg_fee_category, _ = FeeCategory.objects.get_or_create(name='Registration Fee')
                        
                        reg_payment = Payment.objects.create(
                            student=student,
                            total_amount=reg_fee_amount,
                            discount_amount=0,
                            late_fee_amount=0,
                            net_amount=reg_fee_amount,
                            payment_method='cash', # Default
                            payment_status='completed',
                            payment_date=timezone.now().date(),
                            remarks='Registration Fee',
                            collected_by=request.user
                        )
                        
                        PaymentItem.objects.create(
                            payment=reg_payment,
                            fee_category=reg_fee_category,
                            description=f'Registration Fee - {student.get_full_name()}',
                            amount=reg_fee_amount,
                            discount_amount=0,
                            late_fee=0,
                            net_amount=reg_fee_amount
                        )
                        
                        # Add income entry
                        Income.objects.create(
                            perticulers=f"Registration Fee of {student.get_full_name()}",
                            amount=reg_fee_amount,
                            bill_number=reg_payment.payment_id,
                            date=reg_payment.payment_date
                        )

                
                # Create advance payment if advance amount exists
                if advance_amount > 0:
                    advance_category, _ = FeeCategory.objects.get_or_create(name='Advance Payment')
                    
                    advance_payment = Payment.objects.create(
                        student=student,
                        total_amount=advance_amount,
                        discount_amount=0,
                        late_fee_amount=0,
                        net_amount=advance_amount,
                        payment_method='cash',  # Default, can be changed
                        payment_status='completed',
                        payment_date=start_date,
                        remarks=f'Advance payment for {fee_category.name if fee_category else "fees"}',
                        collected_by=request.user
                    )
                    
                    #income saving to db
                    Income.objects.create(perticulers = f"Advance payment of  {str(student.get_full_name())} against {fee_category.name if fee_category else 'fees'}", amount = advance_amount,bill_number = advance_payment.payment_id ,date = start_date )


                    # Create payment item for advance
                    PaymentItem.objects.create(
                        payment=advance_payment,
                        fee_category=advance_category,
                        description=f'Advance Payment - {student.get_full_name()}',
                        amount=advance_amount,
                        discount_amount=0,
                        late_fee=0,
                        net_amount=advance_amount
                    )
                
                # Create installments
                if plan_type == 'custom':
                    for i, inst_data in enumerate(custom_installments):
                         PaymentInstallment.objects.create(
                            payment_plan=payment_plan,
                            installment_number=i + 1,
                            due_date=inst_data['date'],
                            amount=Decimal(str(inst_data['amount'])),
                            status='pending'
                        )
                else:
                    # Logic for auto-generated installments
                    current_date = start_date
                    for i in range(number_of_installments):
                        PaymentInstallment.objects.create(
                            payment_plan=payment_plan,
                            installment_number=i + 1,
                            due_date=current_date,
                            amount=installment_amount,
                            status='pending'
                        )
                        
                        # Calculate next due date based on frequency or plan type
                        if plan_type == 'weekly':
                            current_date += timedelta(weeks=1)
                        elif plan_type == 'monthly': # Monthly
                             # Add a month logic roughly or strict
                             import calendar
                             month = current_date.month - 1 + 1
                             year = current_date.year + month // 12
                             month = month % 12 + 1
                             day = min(current_date.day, calendar.monthrange(year,month)[1])
                             current_date = current_date.replace(year=year, month=month, day=day)
                        elif plan_type == 'quarterly' or plan_type == '3_months':
                             current_date += timedelta(days=90) # Approx
                        elif plan_type == '6_months':
                             current_date += timedelta(days=180) # Approx
                        else:
                             current_date += timedelta(days=installment_frequency)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Payment plan created successfully!',
                        'redirect_url': reverse('student_payment_details', kwargs={'student_id': student.id})
                    })
                
                messages.success(request, 'Payment plan created successfully!')
                return redirect('student_payment_details', student_id=student.id)
                
        except FeeCategory.DoesNotExist:
            error_msg = 'Selected fee category does not exist'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
        except Exception as e:
            error_msg = f'Error creating payment plan: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            messages.error(request, error_msg)
    
    # Get student's fee assignments for calculation
    fee_assignments = StudentFeeAssignment.objects.filter(
        student=student,
        is_active=True
    ).select_related('fee_structure__fee_category')
    
    total_annual_fees = sum(assignment.get_final_amount() for assignment in fee_assignments)
    
    # Get all fee categories
    fee_categories = FeeCategory.objects.all()
    
    context = {
        'student': student,
        'fee_assignments': fee_assignments,
        'total_annual_fees': total_annual_fees,
        'plan_types': PaymentPlan.PLAN_TYPE_CHOICES,
        'session_types': PaymentPlan.SESSION_TYPE_CHOICES,
        'fee_categories': fee_categories,
    }
    
    return render(request, 'payments/create_payment_plan.html', context)



@unauthenticated_user
def student_payment_details(request, student_id):
    """Show detailed payment information for a student"""
    student = get_object_or_404(Student, id=student_id)
    
    # Get payment plans
    # Get payment plans with sorted installments
    payment_plans = PaymentPlan.objects.filter(student=student).order_by('-academic_year').prefetch_related(
        models.Prefetch('installments', queryset=PaymentInstallment.objects.order_by('due_date'))
    )
    
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


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from utils.pdf_generator import render_to_pdf
import tempfile
from .models import Payment, Student

@unauthenticated_user
def generate_invoice(request, payment_id):
    """Generate and display/download invoice for a payment"""
    
    # Get the payment with related data
    payment = get_object_or_404(
        Payment.objects.select_related('student', 'collected_by')
                      .prefetch_related('payment_items__fee_category', 
                                       'payment_items__installment'),
        id=payment_id
    )
    
    # School information
    school_info = {
        'name': 'Blossom British School',
        'address': 'Villa No 2 University Street,',
        'city': 'Ajman UAE',
        'phone': '+971-XXX-XXXXX',  # Add your phone
        'email': 'info@blossombritish.ae',  # Add your email
    }
    
    # Calculate totals
    subtotal = payment.total_amount
    total_discount = payment.discount_amount
    total_late_fee = payment.late_fee_amount
    grand_total = payment.net_amount
    
    context = {
        'payment': payment,
        'student': payment.student,
        'payment_items': payment.payment_items.all(),
        'school': school_info,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'total_late_fee': total_late_fee,
        'grand_total': grand_total,
    }
    
    # Check if PDF download is requested
    if request.GET.get('format') == 'pdf':
        return generate_pdf_invoice(request, context)
    
    # Otherwise, render HTML invoice
    return render(request, 'payments/invoice.html', context)


def generate_pdf_invoice(request, context):
    """Generate PDF version of invoice"""
    
    # Generate PDF
    pdf = render_to_pdf('payments/invoice.html', context)
    
    if pdf:
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{context["payment"].payment_id}.pdf"'
        return response
        
    return HttpResponse("Error generating PDF", status=500)


@unauthenticated_user
def generate_invoice_quick(request, payment_id):
    """Quick invoice generation - returns PDF directly"""
    payment = get_object_or_404(
        Payment.objects.select_related('student', 'collected_by')
                      .prefetch_related('payment_items__fee_category'),
        id=payment_id
    )
    
    school_info = {
        'name': 'Blossom British School',
        'address': 'Villa No 2 University Street,',
        'city': 'Ajman UAE',
        'phone': '+971-504212662',
        'email': 'info@blossombritish.ae',
    }
    
    context = {
        'payment': payment,
        'student': payment.student,
        'payment_items': payment.payment_items.all(),
        'school': school_info,
        'subtotal': payment.total_amount,
        'total_discount': payment.discount_amount,
        'total_late_fee': payment.late_fee_amount,
        'grand_total': payment.net_amount,
    }
    
    return generate_pdf_invoice(request, context)


@csrf_protect
@unauthenticated_user
def edit_payment_plan(request, pk):
    """Edit an existing payment plan"""
    plan = get_object_or_404(PaymentPlan, pk=pk)
    student_id = plan.student.id
    
    if request.method == 'POST':
        form = PaymentPlanEditForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Payment plan for {plan.academic_year} updated successfully.")
            return redirect('student_payment_details', student_id=student_id)
    else:
        form = PaymentPlanEditForm(instance=plan)
    
    context = {
        'form': form,
        'title': f'Edit Payment Plan - {plan.student.get_full_name()}',
        'plan': plan,
        'student': plan.student
    }
    return render(request, 'payments/payment_plan_form.html', context)


@csrf_protect
@unauthenticated_user
def edit_payment_installment(request, pk):
    """Edit a payment installment"""
    installment = get_object_or_404(PaymentInstallment, pk=pk)
    student_id = installment.payment_plan.student.id
    
    if request.method == 'POST':
        form = PaymentInstallmentEditForm(request.POST, instance=installment)
        if form.is_valid():
            form.save()
            # Update status logic ONLY if status wasn't manually changed
            if 'status' not in form.changed_data:
                installment.update_status()
                installment.save()
            
            messages.success(request, f"Installment {installment.installment_number} updated successfully.")
            return redirect('student_payment_details', student_id=student_id)

    else:
        form = PaymentInstallmentEditForm(instance=installment)
    
    context = {
        'form': form,
        'title': f'Edit Installment {installment.installment_number}',
        'installment': installment,
        'student': installment.payment_plan.student 
    }
    return render(request, 'payments/payment_installment_form.html', context)



@csrf_protect
@unauthenticated_user
def delete_payment_installment(request, pk):
    """Delete a pending payment installment"""
    installment = get_object_or_404(PaymentInstallment, pk=pk)
    student_id = installment.payment_plan.student.id
    
    if installment.status != 'pending' and installment.paid_amount > 0:
        messages.error(request, "Cannot delete an installment that has been paid or partially paid.")
        return redirect('student_payment_details', student_id=student_id)

    if request.method == 'POST':
        installment.delete()
        messages.success(request, f"Installment {installment.installment_number} deleted successfully.")
        return redirect('student_payment_details', student_id=student_id)
        
    # If GET, show confirmation page or just redirect (safest is to use POST for deletion)
    # But for simplicity with simple links, we might need a confirmation page or JS handling.
    # Assuming the specific user request implies simple deletion, but POST is safer.
    # I'll implement a simple confirmation template.
    
    context = {
        'title': 'Delete Installment',
        'item_name': f'Installment {installment.installment_number}',
        'cancel_url': 'student_payment_details',
        'cancel_id': student_id
    }
    return render(request, 'payments/confirm_delete.html', context)


@csrf_protect
@unauthenticated_user
def delete_payment_plan(request, pk):
    """Delete a pending payment plan"""
    plan = get_object_or_404(PaymentPlan, pk=pk)
    student_id = plan.student.id
    
    # Check if any installments are paid
    if plan.installments.filter(paid_amount__gt=0).exists():
        messages.error(request, "Cannot delete a payment plan that has paid installments.")
        return redirect('student_payment_details', student_id=student_id)

    if request.method == 'POST':
        plan.delete()
        messages.success(request, f"Payment plan for {plan.academic_year} deleted successfully.")
        return redirect('student_payment_details', student_id=student_id)
        
    context = {
        'title': 'Delete Payment Plan',
        'item_name': f'Payment Plan {plan.academic_year}',
        'cancel_url': 'student_payment_details',
        'cancel_id': student_id
    }
    return render(request, 'payments/confirm_delete.html', context)

@csrf_protect
@unauthenticated_user
def hold_payment_installment(request, pk):
    """Hold a payment installment and transfer balance to next installment"""
    installment = get_object_or_404(PaymentInstallment, pk=pk)
    student_id = installment.payment_plan.student.id
    
    if installment.status == 'held':
        messages.warning(request, "This installment is already on hold.")
        return redirect('student_payment_details', student_id=student_id)

    if request.method == 'POST':
        with transaction.atomic():
            # Find next pending installment
            next_installment = PaymentInstallment.objects.filter(
                payment_plan=installment.payment_plan,
                installment_number__gt=installment.installment_number,
                status='pending'
            ).order_by('installment_number').first()

            if next_installment:
                amount_to_transfer = installment.amount + installment.late_fee - installment.paid_amount
                
                # Update next installment
                next_installment.amount = F('amount') + amount_to_transfer
                next_installment.save()
                next_installment.refresh_from_db() # Reload to get updated amount

                # Update current installment
                installment.status = 'held'
                installment.amount = 0 # Optional: Set to 0 to reflect transfer? Or keep original amount for history? 
                # User request: "AMOUNT IS TRANSFERD TO NEXT MONTH" implies current amount should be gone or 0-ed out effectively.
                # If we set amount to 0, it won't show as due.
                installment.amount = 0
                installment.late_fee = 0 
                installment.save()

                messages.success(request, f"Installment {installment.installment_number} held and amount transferred to Installment {next_installment.installment_number}.")
            else:
                messages.error(request, "No subsequent pending installment found to transfer the amount to.")
        
        return redirect('student_payment_details', student_id=student_id)
        
    context = {
        'title': 'Hold Installment',
        'item_name': f'Installment {installment.installment_number}',
        'cancel_url': 'student_payment_details',
        'cancel_id': student_id,
        'action_verb': 'Hold',
        'message_body': 'Are you sure you want to put this installment on hold? The outstanding amount will be transferred to the next pending installment.'
    }
    return render(request, 'payments/confirm_delete.html', context)


@csrf_protect
@unauthenticated_user
def add_payment_installment(request, plan_id):
    """Add a new installment to an existing payment plan"""
    plan = get_object_or_404(PaymentPlan, pk=plan_id)
    student_id = plan.student.id
    
    if request.method == 'POST':
        form = PaymentInstallmentAddForm(request.POST)
        if form.is_valid():
            installment = form.save(commit=False)
            installment.payment_plan = plan
            
            # Calculate next installment number
            last_installment = plan.installments.order_by('-installment_number').first()
            if last_installment:
                installment.installment_number = last_installment.installment_number + 1
            else:
                installment.installment_number = 1
                
            installment.status = 'pending'
            installment.save()
            
            # Identify source: 'overdue' or 'plan'
            source = request.GET.get('source', '')
            
            messages.success(request, f"Installment {installment.installment_number} added successfully.")
            
            if source == 'overdue':
                return redirect('overdue_report') 
                
            return redirect('student_payment_details', student_id=student_id)
    else:
        form = PaymentInstallmentAddForm()
    
    context = {
        'form': form,
        'title': f'Add Installment - {plan.student.get_full_name()}',
        'plan': plan,
        'student': plan.student
    }
    return render(request, 'payments/payment_installment_form.html', context)
