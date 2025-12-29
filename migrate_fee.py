"""
Standalone script to import payment data from Excel to Django database
Excel Headers: SL No, id, Student Name, Payment Amount, Date, Description, Uniform fee/Books, REMARKS

Usage: python import_payments.py path/to/excel_file.xlsx
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime
import openpyxl

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blossom_school.settings')
django.setup()

# Import models after Django setup
from payments.models import Payment, PaymentItem
from students.models import Student
from home.models import FeeCategory
from Finance.models import Income


def parse_date(date_value):
    """Parse date from Excel in various formats"""
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, str):
        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_value.strip(), fmt).date()
            except ValueError:
                continue
    
    raise ValueError(f"Unable to parse date: {date_value}")


def parse_amount(amount_value):
    """Parse amount from Excel, handling various formats"""
    if amount_value is None or amount_value == '':
        return Decimal('0.00')
    
    if isinstance(amount_value, (int, float)):
        return Decimal(str(amount_value))
    
    if isinstance(amount_value, str):
        # Remove currency symbols and commas
        clean_amount = amount_value.replace('$', '').replace(',', '').replace('₹', '').strip()
        if clean_amount == '' or clean_amount.upper() == 'NA':
            return Decimal('0.00')
        return Decimal(clean_amount)
    
    return Decimal('0.00')


def get_student_by_id_or_name(student_id, student_name):
    """Get student by student_id field or name"""
    # Try by student_id field first
    if student_id:
        try:
            return Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            pass
    
    # Try by name
    if student_name:
        # Try exact match first
        students = Student.objects.filter(
            first_name__iexact=student_name.split()[0] if student_name else ''
        )
        
        if students.exists():
            # If multiple matches, try to match full name
            for student in students:
                if student.get_full_name().lower() == student_name.lower():
                    return student
            # Return first match if no exact full name match
            return students.first()
    
    raise ValueError(f"Student not found: student_id={student_id}, Name={student_name}")


def import_payments_from_excel(excel_path):
    """Main function to import payments from Excel"""
    
    # Load workbook
    print(f"Loading Excel file: {excel_path}")
    workbook = openpyxl.load_workbook(excel_path)
    sheet = workbook.active
    
    # Get fee categories
    try:
        tuition_fee_category = FeeCategory.objects.get(id=5)
        print(f"✓ Tuition Fee Category: {tuition_fee_category.name}")
    except FeeCategory.DoesNotExist:
        print("✗ ERROR: Tuition Fee Category (ID=5) not found!")
        return
    
    try:
        uniform_books_category = FeeCategory.objects.get(id=7)
        print(f"✓ Uniform/Books Category: {uniform_books_category.name}")
    except FeeCategory.DoesNotExist:
        print("✗ ERROR: Uniform/Books Category (ID=7) not found!")
        return
    
    # Get current user (you may need to adjust this)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # Statistics
    success_count = 0
    error_count = 0
    errors = []
    
    # Process each row (skip header)
    print("\nProcessing rows...")
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            # Parse Excel columns
            sl_no = row[0]
            student_id = row[1]
            student_name = row[2]
            payment_amount = parse_amount(row[3])
            date = parse_date(row[4])
            description = row[5] if row[5] else ''
            uniform_books = parse_amount(row[6]) if len(row) > 6 else Decimal('0.00')
            remarks = row[7] if len(row) > 7 and row[7] else ''
            
            # Skip if payment amount is zero and no uniform/books fee
            if payment_amount == 0 and uniform_books == 0:
                print(f"  Row {row_num}: Skipping (no amounts)")
                continue
            
            # Get student
            student = get_student_by_id_or_name(student_id, student_name)
            
            # Calculate totals
            total_amount = payment_amount + uniform_books
            
            # Create Payment record
            payment = Payment.objects.create(
                student=student,
                total_amount=total_amount,
                discount_amount=Decimal('0.00'),
                late_fee_amount=Decimal('0.00'),
                net_amount=total_amount,
                payment_method='cash',  # Default, you can change this
                payment_status='completed',
                payment_date=date,
                remarks=f"{description} | {remarks}".strip(' |'),
                collected_by=admin_user
            )
            
            # Create PaymentItem for tuition fee (Payment Amount)
            if payment_amount > 0:
                PaymentItem.objects.create(
                    payment=payment,
                    fee_category=tuition_fee_category,
                    description=description if description else 'Tuition Fee',
                    amount=payment_amount,
                    discount_amount=Decimal('0.00'),
                    late_fee=Decimal('0.00'),
                    net_amount=payment_amount
                )
                
                # Create Income record for tuition fee
                Income.objects.create(
                    date=date,
                    perticulers=f"{student.get_full_name()} - {tuition_fee_category.name}",
                    amount=float(payment_amount),
                    bill_number=payment.payment_id,
                    other=description if description else ''
                )
            
            # Create PaymentItem for uniform/books if applicable
            if uniform_books > 0:
                PaymentItem.objects.create(
                    payment=payment,
                    fee_category=uniform_books_category,
                    description='Uniform/Books Fee',
                    amount=uniform_books,
                    discount_amount=Decimal('0.00'),
                    late_fee=Decimal('0.00'),
                    net_amount=uniform_books
                )
                
                # Create Income record for uniform/books
                Income.objects.create(
                    date=date,
                    perticulers=f"{student.get_full_name()} - {uniform_books_category.name}",
                    amount=float(uniform_books),
                    bill_number=payment.payment_id,
                    other='Uniform/Books'
                )
            
            success_count += 1
            print(f"  ✓ Row {row_num}: Payment {payment.payment_id} created for {student.get_full_name()} - Amount: ${total_amount}")
            
        except Exception as e:
            error_count += 1
            error_msg = f"Row {row_num}: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
    
    # Summary
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total processed: {success_count + error_count}")
    print(f"✓ Successfully imported: {success_count}")
    print(f"✗ Errors: {error_count}")
    
    if errors:
        print("\nERROR DETAILS:")
        for error in errors:
            print(f"  - {error}")
    
    print("="*60)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_payments.py path/to/excel_file.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        sys.exit(1)
    
    print("="*60)
    print("PAYMENT IMPORT SCRIPT")
    print("="*60)
    
    try:
        import_payments_from_excel(excel_file)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)