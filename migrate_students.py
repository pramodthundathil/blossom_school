"""
Student Data Import Script
Place this file in your project root directory (same level as manage.py)
Run: python import_student_data.py
"""

import os
import django
import pandas as pd
import datetime
from django.utils.dateparse import parse_date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blossom_school.settings')
django.setup()

from students.models import Student, StudentNote, ClassRooms
from django.contrib.auth.models import User


def parse_excel_date(date_value):
    """Parse date from Excel"""
    if pd.isna(date_value) or date_value == '':
        return None
    try:
        if isinstance(date_value, str):
            return parse_date(date_value)
        elif isinstance(date_value, datetime.datetime):
            return date_value.date()
        elif isinstance(date_value, datetime.date):
            return date_value
    except:
        return None
    return None


def get_value(row, column_name):
    """Safely get value from row"""
    try:
        value = row.get(column_name, '')
        if pd.isna(value) or value == '':
            return None
        return str(value).strip()
    except:
        return None


def import_students():
    """Import students from Excel file"""
    
    excel_file = 'ADMISSION_DETAILS_2025.xlsx'
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        print(f'Reading {len(df)} rows from Excel file...\n')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        notes_created = 0
        
        for index, row in df.iterrows():
            try:
                # Extract child name
                child_name = get_value(row, 'CHILD NAME')
                if child_name and ' ' in child_name:
                    name_parts = child_name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1]
                else:
                    first_name = child_name or 'Unknown'
                    last_name = 'Unknown'
                
                # Parse dates
                date_of_birth = parse_excel_date(get_value(row, 'DATE OF BIRTH'))
                date_of_admission = parse_excel_date(get_value(row, 'DATE OF ADMISSION'))
                date_start = parse_excel_date(get_value(row, 'started from'))
                
                # Get other fields
                nationality = get_value(row, 'NATIONALITY') or 'Not Specified'
                age_value = get_value(row, 'AGE OF ENROLLMENT)')
                
                age_at_enrollment = None
                if age_value:
                    try:
                        age_at_enrollment = int(float(age_value))
                    except:
                        pass
                
                father_mobile = get_value(row, 'FATHER NO') or ''
                mother_mobile = get_value(row, 'MOTHER NO') or ''
                notes_text = get_value(row, 'notes')  # Changed from COMMENTS to notes
                transportation = get_value(row, 'TRANSPORTATION') or ''
                sl_no = get_value(row, 'SL NO')
                
                # Check if student already exists
                existing_student = Student.objects.filter(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth
                ).first()
                
                if existing_student:
                    # Update existing student
                    existing_student.nationality = nationality
                    existing_student.age_at_enrollment = age_at_enrollment
                    existing_student.father_mobile = father_mobile
                    existing_student.mother_mobile = mother_mobile
                    if transportation:
                        existing_student.hours_required = transportation
                    if date_start:
                        existing_student.date_start = date_start
                    
                    existing_student.save()
                    
                    # Add or update note
                    if notes_text:
                        # Check if note already exists with same text
                        existing_note = StudentNote.objects.filter(
                            student=existing_student,
                            note=notes_text
                        ).first()
                        
                        if not existing_note:
                            StudentNote.objects.create(
                                student=existing_student,
                                note=notes_text,
                                is_important=False
                            )
                            notes_created += 1
                    
                    updated_count += 1
                    print(f'✓ Updated: {existing_student.get_full_name()} (ID: {existing_student.student_id})')
                    if notes_text:
                        print(f'  └─ Note added: {notes_text[:50]}...')
                else:
                    # Create new student
                    student = Student.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        nationality=nationality,
                        gender='M',  # Default gender
                        date_of_birth=date_of_birth or datetime.date(2020, 1, 1),
                        age_at_enrollment=age_at_enrollment,
                        
                        # Father info
                        father_name='Not Provided',
                        father_nationality=nationality,
                        father_mobile=father_mobile,
                        
                        # Mother info
                        mother_name='Not Provided',
                        mother_nationality=nationality,
                        mother_mobile=mother_mobile,
                        
                        # Home info (required fields)
                        full_home_address='Not Provided',
                        
                        # Emergency contact (required fields)
                        first_contact_person='Emergency Contact',
                        first_contact_relationship='Parent',
                        first_contact_telephone=father_mobile or mother_mobile or '0000000000',
                        
                        # School info
                        year_of_admission=datetime.datetime.now().year,
                        date_start=date_start,
                        status='enrolled',
                        is_active=True,
                        
                        # Optional fields
                        hours_required=transportation,
                    )
                    created_count += 1
                    print(f'✓ Created: {student.get_full_name()} - {student.student_id}')
                    
                    # Create note if exists
                    if notes_text:
                        StudentNote.objects.create(
                            student=student,
                            note=notes_text,
                            is_important=False
                        )
                        notes_created += 1
                        print(f'  └─ Note added: {notes_text[:50]}...')
                    
            except Exception as e:
                error_count += 1
                print(f'✗ Error on row {index + 2}: {str(e)}')
        
        # Summary
        print('\n' + '='*50)
        print('IMPORT SUMMARY')
        print('='*50)
        print(f'Students Created: {created_count}')
        print(f'Students Updated: {updated_count}')
        print(f'Notes Created: {notes_created}')
        print(f'Errors: {error_count}')
        print('='*50)
        
    except FileNotFoundError:
        print(f'ERROR: File "{excel_file}" not found!')
        print('Please make sure the file is in the same directory as this script.')
    except Exception as e:
        print(f'ERROR: Failed to read Excel file: {str(e)}')


if __name__ == '__main__':
    print('Starting student data import...\n')
    import_students()
    print('\nImport completed!')