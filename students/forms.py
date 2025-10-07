from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from datetime import date, datetime
import re
from .models import Student, StudentDocument

class StudentForm(forms.ModelForm):
    # Custom validators
    phone_validator = RegexValidator(
        regex=r'^[\+]?[\d\s\-\(\)]+$',
        message="Please enter a valid phone number"
    )
    
    name_validator = RegexValidator(
        regex=r"^[a-zA-Z\s'-]+$",
        message="Name can only contain letters, spaces, hyphens and apostrophes"
    )
    
    emirates_id_validator = RegexValidator(
        regex=r'^\d{15}$',
        message="Emirates ID should be exactly 15 digits"
    )
    
    class Meta:
        model = Student
        exclude = ['created_by', 'student_id', 'is_active']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_start': forms.DateInput(attrs={'type': 'date'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}),
            'parent_signature_date': forms.DateInput(attrs={'type': 'date'}),
            'full_home_address': forms.Textarea(attrs={'rows': 3}),
            'siblings_info': forms.Textarea(attrs={'rows': 3}),
            'languages_spoken': forms.Textarea(attrs={'rows': 2}),
            'term_to_begin': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply base styling and setup
        for field_name, field in self.fields.items():
            widget = field.widget

            # Apply base CSS class
            current_classes = widget.attrs.get('class', '')
            widget.attrs.update({
                "class": f"form-input {current_classes}".strip(),
                "id": f"id_{field_name}"
            })

            # Set specific input types
            if isinstance(field, forms.DateField):
                widget.attrs['type'] = 'date'
            elif isinstance(field, forms.EmailField):
                widget.attrs['type'] = 'email'
            elif isinstance(field, forms.IntegerField):
                widget.attrs['type'] = 'number'
                if field_name == 'age_at_enrollment':
                    widget.attrs.update({'min': '1', 'max': '18'})
                elif field_name == 'year_of_admission':
                    current_year = datetime.now().year
                    widget.attrs.update({
                        'min': str(current_year - 1), 
                        'max': str(current_year + 2)
                    })
            elif isinstance(field, forms.ImageField):
                widget.attrs.update({
                    'type': 'file',
                    'accept': 'image/jpeg,image/png,image/gif,image/webp'
                })

        # Add custom validators to specific fields
        self.fields['first_name'].validators.append(self.name_validator)
        self.fields['last_name'].validators.append(self.name_validator)
        self.fields['father_name'].validators.append(self.name_validator)
        self.fields['mother_name'].validators.append(self.name_validator)
        
        # Phone number validators
        phone_fields = [
            'father_mobile', 'mother_mobile', 'phone_number', 'home_telephone',
            'father_work_telephone', 'mother_work_telephone', 
            'first_contact_telephone', 'second_contact_telephone'
        ]
        for field_name in phone_fields:
            if field_name in self.fields:
                self.fields[field_name].validators.append(self.phone_validator)
        
        # Emirates ID validator
        if 'child_emirates_id' in self.fields:
            self.fields['child_emirates_id'].validators.append(self.emirates_id_validator)
        
        # Set default values
        if not self.instance.pk:  # Only for new records
            current_year = datetime.now().year
            if 'year_of_admission' in self.fields:
                self.fields['year_of_admission'].initial = current_year
            if 'city' in self.fields:
                self.fields['city'].initial = 'Dubai'
        
        # Add placeholders and help text
        placeholders = {
            'first_name': 'Enter child\'s first name',
            'last_name': 'Enter child\'s last name',
            'family_name': 'Enter family name (optional)',
            'nationality': 'e.g., UAE, Indian, Pakistani',
            'father_name': 'Enter father\'s full name',
            'mother_name': 'Enter mother\'s full name',
            'father_email': 'father@example.com',
            'mother_email': 'mother@example.com',
            'email': 'primary@example.com',
            'father_mobile': '+971 50 123 4567',
            'mother_mobile': '+971 50 123 4567',
            'phone_number': '+971 50 123 4567',
            'child_emirates_id': '784-1234-1234567-01',
            'po_box_number': 'P.O. Box 12345',
            'city': 'Dubai',
            'languages_spoken': 'English, Arabic, Hindi',
            'siblings_info': 'Name: John, Age: 10\nName: Jane, Age: 8',
        }
        
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if first_name and len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters long")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if last_name and len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters long")
        return last_name

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if dob >= today:
                raise ValidationError("Date of birth cannot be in the future")
            if age < 1:
                raise ValidationError("Child must be at least 1 year old")
            if age > 18:
                raise ValidationError("Child must be under 18 years old")
        return dob

    def clean_age_at_enrollment(self):
        age = self.cleaned_data.get('age_at_enrollment')
        dob = self.cleaned_data.get('date_of_birth')
        
        if age is not None:
            if age < 1 or age > 18:
                raise ValidationError("Age must be between 1 and 18")
            
            # Cross-validate with date of birth if provided
            if dob:
                today = date.today()
                calculated_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                
                if abs(calculated_age - age) > 1:
                    raise ValidationError(
                        f"Age ({age}) doesn't match the date of birth provided (calculated age: {calculated_age})"
                    )
        
        return age

    def clean_year_of_admission(self):
        year = self.cleaned_data.get('year_of_admission')
        if year:
            current_year = datetime.now().year
            if year < current_year - 1 or year > current_year + 2:
                raise ValidationError(
                    f"Year of admission must be between {current_year - 1} and {current_year + 2}"
                )
        return year

    def clean_father_email(self):
        email = self.cleaned_data.get('father_email', '').strip()
        if email:
            # Additional email validation
            try:
                EmailValidator()(email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address")
        return email

    def clean_mother_email(self):
        email = self.cleaned_data.get('mother_email', '').strip()
        if email:
            try:
                EmailValidator()(email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address")
        return email

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            try:
                EmailValidator()(email)
            except ValidationError:
                raise ValidationError("Please enter a valid email address")
        return email

    def clean_child_emirates_id(self):
        emirates_id = self.cleaned_data.get('child_emirates_id', '').strip()
        if emirates_id:
            # Remove any non-digit characters for validation
            digits_only = re.sub(r'\D', '', emirates_id)
            if len(digits_only) != 15:
                raise ValidationError("Emirates ID must be exactly 15 digits")
            return emirates_id
        return emirates_id

    def validate_phone_number(self, phone_number, field_name):
        """Helper method to validate phone numbers"""
        if phone_number:
            # Remove all non-digit characters to count digits
            digits_only = re.sub(r'\D', '', phone_number)
            if len(digits_only) < 7:
                raise ValidationError(f"{field_name} must contain at least 7 digits")
            if not re.match(r'^[\+]?[\d\s\-\(\)]+$', phone_number):
                raise ValidationError(f"Please enter a valid {field_name.lower()}")
        return phone_number

    def clean_father_mobile(self):
        return self.validate_phone_number(
            self.cleaned_data.get('father_mobile', '').strip(), 
            'Father\'s mobile number'
        )

    def clean_mother_mobile(self):
        return self.validate_phone_number(
            self.cleaned_data.get('mother_mobile', '').strip(), 
            'Mother\'s mobile number'
        )

    def clean_phone_number(self):
        return self.validate_phone_number(
            self.cleaned_data.get('phone_number', '').strip(), 
            'Phone number'
        )

    def clean_first_contact_telephone(self):
        return self.validate_phone_number(
            self.cleaned_data.get('first_contact_telephone', '').strip(), 
            'First contact telephone'
        )

    def clean_second_contact_telephone(self):
        return self.validate_phone_number(
            self.cleaned_data.get('second_contact_telephone', '').strip(), 
            'Second contact telephone'
        )

    def clean_child_photo(self):
        photo = self.cleaned_data.get('child_photo')
        if photo:
            return self.validate_image_file(photo, 'Child photo')
        return photo

    def clean_father_photo(self):
        photo = self.cleaned_data.get('father_photo')
        if photo:
            return self.validate_image_file(photo, 'Father photo')
        return photo

    def clean_mother_photo(self):
        photo = self.cleaned_data.get('mother_photo')
        if photo:
            return self.validate_image_file(photo, 'Mother photo')
        return photo

    def validate_image_file(self, file, field_name):
        """Helper method to validate image files"""
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError(f"{field_name} file size must be less than 5MB")
            
            # # Check file type
            # allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            # if file.content_type not in allowed_types:
            #     raise ValidationError(
            #         f"{field_name} must be a valid image file (JPEG, PNG, GIF, WEBP)"
            #     )
            
            # Additional validation for image content
            try:
                from PIL import Image
                image = Image.open(file)
                image.verify()  # Verify it's a valid image
                file.seek(0)  # Reset file pointer
            except Exception:
                raise ValidationError(f"{field_name} appears to be corrupted or is not a valid image")
        
        return file

    def clean_date_start(self):
        start_date = self.cleaned_data.get('date_start')
        if start_date:
            today = date.today()
            if start_date < today:
                # Allow past dates but warn if too far in the past
                days_diff = (today - start_date).days
                if days_diff > 365:  # More than a year ago
                    raise ValidationError("Start date seems too far in the past")
        return start_date

    def clean_date_end(self):
        end_date = self.cleaned_data.get('date_end')
        start_date = self.cleaned_data.get('date_start')
        
        if end_date and start_date:
            if end_date <= start_date:
                raise ValidationError("End date must be after start date")
        
        return end_date

    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        
        # Ensure at least one email is provided
        father_email = cleaned_data.get('father_email', '').strip()
        mother_email = cleaned_data.get('mother_email', '').strip()
        primary_email = cleaned_data.get('email', '').strip()
        
        if not father_email and not mother_email and not primary_email:
            raise ValidationError({
                'father_email': 'At least one email address must be provided (father, mother, or primary)'
            })
        
        # Ensure at least one phone number is provided
        father_mobile = cleaned_data.get('father_mobile', '').strip()
        mother_mobile = cleaned_data.get('mother_mobile', '').strip()
        home_telephone = cleaned_data.get('home_telephone', '').strip()
        primary_phone = cleaned_data.get('phone_number', '').strip()
        
        if not father_mobile and not mother_mobile and not home_telephone and not primary_phone:
            raise ValidationError({
                'father_mobile': 'At least one contact number must be provided'
            })
        
        # Validate emergency contact information
        first_contact_person = cleaned_data.get('first_contact_person', '').strip()
        first_contact_telephone = cleaned_data.get('first_contact_telephone', '').strip()
        
        if first_contact_person and not first_contact_telephone:
            raise ValidationError({
                'first_contact_telephone': 'Telephone is required when contact person is provided'
            })
        
        # Auto-fill primary email if not provided
        if not primary_email:
            if father_email:
                cleaned_data['email'] = father_email
            elif mother_email:
                cleaned_data['email'] = mother_email
        
        # Auto-fill primary phone if not provided
        if not primary_phone:
            if father_mobile:
                cleaned_data['phone_number'] = father_mobile
            elif mother_mobile:
                cleaned_data['phone_number'] = mother_mobile
        
        # Calculate age at enrollment if not provided but date of birth is available
        dob = cleaned_data.get('date_of_birth')
        age_at_enrollment = cleaned_data.get('age_at_enrollment')
        
        if dob and not age_at_enrollment:
            today = date.today()
            calculated_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if 1 <= calculated_age <= 18:
                cleaned_data['age_at_enrollment'] = calculated_age
        
        return cleaned_data

    def save(self, commit=True):
        """Custom save method with additional processing"""
        instance = super().save(commit=False)
        
        # Set status to pending by default
        if not instance.pk:
            instance.status = 'pending'
            instance.approved = False
        
        if commit:
            instance.save()
        
        return instance


# Additional form for quick student search/filter
class StudentSearchForm(forms.Form):
    SEARCH_CHOICES = [
        ('', 'All Fields'),
        ('name', 'Name'),
        ('student_id', 'Student ID'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('city', 'City'),
    ]
    
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
    ]
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search students...',
            'class': 'form-control'
        })
    )
    
    search_field = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    year_of_admission = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Year',
            'class': 'form-control'
        })
    )


class DocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument   # don't forget to set model
        fields = ["document_type", "document"]

        widgets = {
            "document_type": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "document": forms.FileInput(
                attrs={
                    "class": "form-input",
                }
            ),
        }



from .models import Transportation

class TransportationForm(forms.ModelForm):
    class Meta:
        model = Transportation
        fields = ['destination', 'school', 'amount']
        widgets = {
            'school': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-input'}),
            'student': forms.Select(attrs={'class': 'form-input'}),
            'destination': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prepopulate school field
        self.fields['school'].initial = 'Blossom British School Ajman UAE'
