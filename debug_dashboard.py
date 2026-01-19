import os
import django
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blossom_school.settings')
django.setup()

from students.models import Student
from utils.models import Teacher, Attendance
from payments.models import Payment, PaymentInstallment
from home.models import ClassRooms
from Finance.models import Expense, Income

def test_dashboard_data():
    print("Starting dashboard data test...")
    try:
        # Get current date info
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        print(f"Date: {today}, Month: {current_month}, Year: {current_year}")

        # STUDENT STATISTICS
        total_students = Student.objects.all().count()
        print(f"Total Students: {total_students}")
        
        students_by_status = Student.objects.values('status').annotate(count=Count('id'))
        print(f"Students by Status: {list(students_by_status)}")

        # PAYMENT STATISTICS
        payments_this_month = Payment.objects.filter(
            payment_date__month=current_month,
            payment_date__year=current_year,
            payment_status='completed'
        )
        total_revenue = payments_this_month.aggregate(total=Sum('net_amount'))['total'] or Decimal('0')
        print(f"Total Revenue: {total_revenue}")
        
        # PaymentInstallment check
        pending = PaymentInstallment.objects.filter(status='pending').count()
        print(f"Pending Installments: {pending}")
        
        # REVENUE TREND
        print("\nChecking Trends loop:")
        for i in range(5, -1, -1):
            month_date = (today.replace(day=1) - timedelta(days=i*30))
            month = month_date.month
            year = month_date.year
            print(f"Month {i} ago: {month}/{year}")
            
            # This line caused concern in logic review, let's test it
            month_revenue = Payment.objects.filter(
                payment_date__month=month,
                payment_date__year=year,
                payment_status='completed'
            ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0')
            print(f"  Revenue: {month_revenue}")

        print("\nTest completed successfully.")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_data()
