import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.urls import reverse
from PIL import Image
import os
from home.models import ClassRooms


User  = get_user_model()

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    DAYS_CHOICES = [
        ('2_days', '2 Days'),
        ('3_days', '3 Days'),
        ('4_days', '4 Days'),
        ('5_days', '5 Days'),
        ('6_days', '6 Days'),
        ('full_week', 'Full Week'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Child Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    age_at_enrollment = models.IntegerField(blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True)
    child_emirates_id = models.CharField(max_length=20, blank=True)
    languages_spoken = models.TextField(blank=True)
    
    # Photos
    child_photo = models.ImageField(upload_to='student_photos/child/', blank=True, null=True)
    mother_photo = models.ImageField(upload_to='student_photos/mother/', blank=True, null=True)
    father_photo = models.ImageField(upload_to='student_photos/father/', blank=True, null=True)
    
    # Father Information
    father_name = models.CharField(max_length=100)
    father_nationality = models.CharField(max_length=100)
    father_place_of_work = models.CharField(max_length=200, blank=True)
    father_position_held = models.CharField(max_length=200, blank=True)
    father_mobile = models.CharField(max_length=20, blank=True)
    father_work_telephone = models.CharField(max_length=20, blank=True)
    father_email = models.EmailField(blank=True)
    
    # Mother Information
    mother_name = models.CharField(max_length=100)
    mother_nationality = models.CharField(max_length=100)
    mother_place_of_work = models.CharField(max_length=200, blank=True)
    mother_position_held = models.CharField(max_length=200, blank=True)
    mother_mobile = models.CharField(max_length=20, blank=True)
    mother_work_telephone = models.CharField(max_length=20, blank=True)
    mother_email = models.EmailField(blank=True)
    
    # Siblings Information
    siblings_info = models.TextField(blank=True, help_text="Sibling names and ages")
    
    # Home Information
    home_telephone = models.CharField(max_length=20, blank=True)
    full_home_address = models.TextField()
    po_box_number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, default='Dubai')
    
    # Emergency Contacts
    first_contact_person = models.CharField(max_length=100)
    first_contact_relationship = models.CharField(max_length=50)
    first_contact_telephone = models.CharField(max_length=20)
    
    second_contact_person = models.CharField(max_length=100, blank=True)
    second_contact_relationship = models.CharField(max_length=50, blank=True)
    second_contact_telephone = models.CharField(max_length=20, blank=True)
    
    # School Information
    term_to_begin = models.TextField(null=True, blank=True)
    days_per_week = models.CharField(max_length=10, choices=DAYS_CHOICES, default="5_days")
    hours_required = models.CharField(max_length=200, blank=True)
    class_room = models.ForeignKey(ClassRooms, on_delete=models.SET_NULL, null=True, blank=True)

    # Status and Administrative
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',null=True, blank=True)
    approved = models.BooleanField(default=False)
    year_of_admission = models.IntegerField()
    date_start = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    
    # Contact Information (for main contact)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Parent signature and date
    parent_signature_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.student_id}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        
        if not self.email and self.father_email:
            self.email = self.father_email
        elif not self.email and self.mother_email:
            self.email = self.mother_email
            
        if not self.phone_number and self.father_mobile:
            self.phone_number = self.father_mobile
        elif not self.phone_number and self.mother_mobile:
            self.phone_number = self.mother_mobile
            
        super().save(*args, **kwargs)
    
    def generate_student_id(self):
        """Generate unique student ID"""
        import datetime
        year = datetime.datetime.now().year
        last_student = Student.objects.filter(
            student_id__startswith=f'BS{year}'
        ).order_by('-student_id').first()
        
        if last_student:
            last_number = int(last_student.student_id[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'BS{year}{new_number:04d}'


class StudentDocument(models.Model):
    DOCUMENT_TYPES = [
        ('birth_certificate', 'Birth Certificate'),
        ('passport', 'Passport Copy'),
        ('emirates_id', 'Emirates ID'),
        ('medical_records', 'Medical Records'),
        ('previous_school_records', 'Previous School Records'),
        ('photo', 'Passport Photo'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to='student_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.get_document_type_display()}"


class StudentNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.student.get_full_name()}"