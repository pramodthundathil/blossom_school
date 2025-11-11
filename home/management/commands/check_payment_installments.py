# management/commands/check_payment_installments.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from payments.models import PaymentInstallment
from students.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Check for upcoming and overdue payment installments and create notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days before due date to send upcoming payment notification (default: 3)'
        )

    def handle(self, *args, **options):
        days_before = options['days']
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=days_before)

        self.stdout.write(self.style.SUCCESS(f'Starting payment installment check...'))
        self.stdout.write(f'Today: {today}')
        self.stdout.write(f'Checking for payments due on: {upcoming_date}')

        # Check for overdue payments
        overdue_count = self.check_overdue_installments(today)
        
        # Check for upcoming payments
        upcoming_count = self.check_upcoming_installments(today, upcoming_date)
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCompleted! Created {overdue_count} overdue and {upcoming_count} upcoming notifications.'
        ))

    def check_overdue_installments(self, today):
        """Check for overdue installments and create notifications"""
        # First, let's see ALL installments that are past due
        all_past_due = PaymentInstallment.objects.filter(
            due_date__lte=today
        ).exclude(
            status='paid'  # Only exclude fully paid installments
        ).select_related('payment_plan', 'payment_plan__student')
        
        self.stdout.write(f'\nChecking overdue installments...')
        self.stdout.write(f'Total installments with due_date <= {today} (excluding paid): {all_past_due.count()}')
        
        # Show details of all past due installments
        for inst in all_past_due:
            self.stdout.write(
                f'  - {inst.payment_plan.student.get_full_name()} | '
                f'Installment #{inst.installment_number} | '
                f'Due: {inst.due_date} | '
                f'Status: {inst.status} | '
                f'is_overdue: {inst.is_overdue} | '
                f'Amount: ₹{inst.amount} | '
                f'Paid: ₹{inst.paid_amount}'
            )
        
        # Now filter for installments that need to be marked as overdue
        overdue_installments = all_past_due.filter(
            status__in=['pending', 'partially_paid', 'overdue']  # Include 'overdue' status too
        )

        self.stdout.write(f'\nInstallments to process: {overdue_installments.count()}')

        count = 0
        for installment in overdue_installments:
            # Track if this is newly marked as overdue
            was_not_overdue = not installment.is_overdue
            
            # Calculate days overdue
            days_overdue = (today - installment.due_date).days
            
            self.stdout.write(
                f'\nProcessing: {installment.payment_plan.student.get_full_name()} - '
                f'Installment #{installment.installment_number} - '
                f'Due: {installment.due_date} ({days_overdue} days overdue) - '
                f'Status: {installment.status} - '
                f'Already marked overdue: {installment.is_overdue}'
            )
            
            # Update installment status
            installment.is_overdue = True
            if installment.paid_amount == 0:
                installment.status = 'overdue'
            else:
                installment.status = 'partially_paid'
            installment.save(update_fields=['is_overdue', 'status'])
            
            self.stdout.write(f'  Updated status to: {installment.status}, is_overdue: True')

            # Get all staff users or assign to created_by user
            users_to_notify = self.get_users_to_notify(installment)
            
            self.stdout.write(f'  Users to notify: {len(users_to_notify)} user(s)')

            for user in users_to_notify:
                # Only create notification if this installment was just marked as overdue
                # or if no overdue notification exists yet
                existing_notification = Notification.objects.filter(
                    user=user,
                    installment=installment,
                    notification_type='overdue'
                ).exists()
                
                self.stdout.write(f'    Checking user: {user.username} - Existing notification: {existing_notification}')

                if not existing_notification:
                    # Determine priority based on days overdue
                    if days_overdue > 30:
                        priority = 'urgent'
                    elif days_overdue > 14:
                        priority = 'high'
                    else:
                        priority = 'medium'

                    outstanding = installment.get_outstanding_amount()
                    
                    try:
                        notification = Notification.objects.create(
                            user=user,
                            student=installment.payment_plan.student,
                            installment=installment,
                            notification_type='overdue',
                            priority=priority,
                            title=f'Overdue Payment - {installment.payment_plan.student.get_full_name()}',
                            message=(
                                f'Installment #{installment.installment_number} is {days_overdue} days overdue. '
                                f'Due date: {installment.due_date.strftime("%d %b %Y")}. '
                                f'Outstanding amount: ₹{outstanding:.2f}'
                            )
                        )
                        count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'    ✓ Created overdue notification for {user.username}'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'    ✗ Error creating notification for {user.username}: {str(e)}'
                            )
                        )
                else:
                    self.stdout.write(f'    - Skipped (notification already exists)')

        return count

    def check_upcoming_installments(self, today, upcoming_date):
        """Check for upcoming installments and create notifications"""
        upcoming_installments = PaymentInstallment.objects.filter(
            due_date=upcoming_date,
            status='pending'
        ).select_related('payment_plan', 'payment_plan__student')

        count = 0
        for installment in upcoming_installments:
            users_to_notify = self.get_users_to_notify(installment)

            for user in users_to_notify:
                # Check if notification already exists
                existing_notification = Notification.objects.filter(
                    user=user,
                    installment=installment,
                    notification_type='upcoming'
                ).exists()

                if not existing_notification:
                    notification = Notification.objects.create(
                        user=user,
                        student=installment.payment_plan.student,
                        installment=installment,
                        notification_type='upcoming',
                        priority='medium',
                        title=f'Upcoming Payment - {installment.payment_plan.student.get_full_name()}',
                        message=(
                            f'Installment #{installment.installment_number} is due in 3 days. '
                            f'Due date: {installment.due_date.strftime("%d %b %Y")}. '
                            f'Amount: ₹{installment.amount:.2f}'
                        )
                    )
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Created upcoming notification for {installment.payment_plan.student.get_full_name()} '
                            f'(Installment #{installment.installment_number})'
                        )
                    )

        return count

    def get_users_to_notify(self, installment):
        """Get list of users to notify for this installment"""
        users = []
        
        # Notify the user who created the payment plan
        if installment.payment_plan.created_by:
            users.append(installment.payment_plan.created_by)
        
        # Notify all staff/admin users
        staff_users = User.objects.filter(is_staff=True, is_active=True)
        users.extend(staff_users)
        
        # Remove duplicates
        return list(set(users))