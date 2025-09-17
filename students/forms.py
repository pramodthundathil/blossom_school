# forms.py
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from django.core.exceptions import ValidationError
from .models import Student, Parent, EmergencyContact, Document
import datetime

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['id', 'student_id', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'intended_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name (Optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44 7xxx xxx xxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SW1A 1AA'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'United Kingdom'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'British'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Passport Number (Optional)'}),
            'visa_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Visa Status (Optional)'}),
            'year_group': forms.Select(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Previous School (Optional)'}),
            'previous_school_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Previous School Address (Optional)'}),
            'has_sen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sen_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please provide details of special educational needs'}),
            'has_ehcp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any medical conditions'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any allergies'}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Current medications'}),
            'emergency_medical_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Emergency medical information'}),
            'dietary_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dietary requirements'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        if dob > datetime.date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        
        # Check if student is too young or too old for school
        age = (datetime.date.today() - dob).days // 365
        if age < 10 or age > 19:
            raise ValidationError("Student age must be between 10 and 19 years.")
        
        return dob
    
    def clean_intended_start_date(self):
        start_date = self.cleaned_data['intended_start_date']
        if start_date < datetime.date.today():
            raise ValidationError("Intended start date cannot be in the past.")
        return start_date
    
    def clean_postcode(self):
        postcode = self.cleaned_data['postcode'].upper().replace(' ', '')
        # Basic UK postcode validation
        import re
        uk_postcode_pattern = r'^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$'
        if postcode and not re.match(uk_postcode_pattern, postcode):
            raise ValidationError("Please enter a valid UK postcode.")
        
        # Add space back in correct position
        if len(postcode) >= 3:
            postcode = postcode[:-3] + ' ' + postcode[-3:]
        
        return postcode


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        exclude = ['id', 'student', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mr/Mrs/Ms/Dr'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44 7xxx xxx xxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'parent@example.com'}),
            'same_address_as_student': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SW1A 1AA'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}),
            'employer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employer'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44 20 xxxx xxxx'}),
            'is_emergency_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_parental_responsibility': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make address fields required when same_address_as_student is False
        self.fields['same_address_as_student'].initial = True


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        exclude = ['id', 'student', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship to Student'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44 7xxx xxx xxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'emergency@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = ['id', 'student', 'uploaded_at', 'uploaded_by']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Document Description (Optional)'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }


# Formsets for handling multiple related objects
ParentFormSet = inlineformset_factory(
    Student, 
    Parent, 
    form=ParentForm, 
    extra=2, 
    can_delete=True,
    min_num=1,
    validate_min=True
)

EmergencyContactFormSet = inlineformset_factory(
    Student, 
    EmergencyContact, 
    form=EmergencyContactForm, 
    extra=2, 
    can_delete=True,
    min_num=1,
    validate_min=True
)

DocumentFormSet = inlineformset_factory(
    Student, 
    Document, 
    form=DocumentForm, 
    extra=1, 
    can_delete=True
)


class StudentSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Search by name, student ID, or email...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Student.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    year_group = forms.ChoiceField(
        choices=[('', 'All Year Groups')] + Student.YEAR_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DisableStudentForm(forms.ModelForm):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please provide reason for disabling this student record...'
        }),
        required=True,
        help_text="This field is required when disabling a student."
    )
    
    class Meta:
        model = Student
        fields = ['status', 'is_active']
        widgets = {
            'status': forms.HiddenInput(),
            'is_active': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'disabled'
        self.fields['is_active'].initial = False