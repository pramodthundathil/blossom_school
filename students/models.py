# models.py
from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
import uuid
from django.contrib.auth import get_user_model


User = get_user_model()

class Student(models.Model):
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal Details
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True)
    
    # Address
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United Kingdom')
    
    # Nationality and Immigration
    nationality = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50, blank=True)
    visa_status = models.CharField(max_length=100, blank=True)
    
    # Academic Information
    YEAR_GROUP_CHOICES = [
        ('Y7', 'Year 7'),
        ('Y8', 'Year 8'),
        ('Y9', 'Year 9'),
        ('Y10', 'Year 10'),
        ('Y11', 'Year 11'),
        ('Y12', 'Year 12 (Sixth Form)'),
        ('Y13', 'Year 13 (Sixth Form)'),
    ]
    year_group = models.CharField(max_length=3, choices=YEAR_GROUP_CHOICES)
    intended_start_date = models.DateField()
    previous_school = models.CharField(max_length=255, blank=True)
    previous_school_address = models.TextField(blank=True)
    
    # Special Educational Needs
    has_sen = models.BooleanField(default=False, verbose_name="Has Special Educational Needs")
    sen_details = models.TextField(blank=True, verbose_name="SEN Details")
    has_ehcp = models.BooleanField(default=False, verbose_name="Has Education, Health and Care Plan")
    
    # Medical Information
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    emergency_medical_info = models.TextField(blank=True)
    
    # Dietary Requirements
    dietary_requirements = models.TextField(blank=True)
    
    # Status and Metadata
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlist', 'Waitlisted'),
        ('enrolled', 'Enrolled'),
        ('disabled', 'Disabled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Photo
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['status']),
            models.Index(fields=['year_group']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    
    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate student ID automatically
            year = self.intended_start_date.year if self.intended_start_date else 2024
            last_student = Student.objects.filter(
                student_id__startswith=f"STU{year}"
            ).order_by('-student_id').first()
            
            if last_student:
                last_number = int(last_student.student_id[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.student_id = f"STU{year}{new_number:04d}"
        
        super().save(*args, **kwargs)


class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    
    # Personal Details
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    RELATIONSHIP_CHOICES = [
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('guardian', 'Guardian'),
        ('step_mother', 'Step Mother'),
        ('step_father', 'Step Father'),
        ('grandparent', 'Grandparent'),
        ('other', 'Other'),
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    
    # Address (if different from student)
    same_address_as_student = models.BooleanField(default=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    
    # Professional Information
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=255, blank=True)
    work_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Emergency Contact
    is_emergency_contact = models.BooleanField(default=True)
    
    # Parental Responsibility
    has_parental_responsibility = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['relationship', 'last_name', 'first_name']
        unique_together = ['student', 'email']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_relationship_display()})"
    
    def get_full_name(self):
        if self.title:
            return f"{self.title} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class EmergencyContact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='emergency_contacts')
    
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=17)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Priority order
    priority = models.PositiveIntegerField(default=1, help_text="1 = Primary, 2 = Secondary, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'name']
        unique_together = ['student', 'priority']
    
    def __str__(self):
        return f"{self.name} - {self.relationship} (Priority {self.priority})"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    
    DOCUMENT_TYPE_CHOICES = [
        ('birth_certificate', 'Birth Certificate'),
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('school_report', 'School Report'),
        ('medical_report', 'Medical Report'),
        ('sen_report', 'SEN Report'),
        ('ehcp', 'Education, Health and Care Plan'),
        ('other', 'Other'),
    ]
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='student_documents/')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_document_type_display()}"