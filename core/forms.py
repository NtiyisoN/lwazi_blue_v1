from django import forms
from .models import (
    InternProfile, EmployerProfile, InternDocument,
    Education, WorkExperience, Skill, Industry, Location
)


class InternProfileForm(forms.ModelForm):
    """Form for intern profile creation and editing"""
    
    class Meta:
        model = InternProfile
        fields = [
            'full_name', 'phone', 'date_of_birth', 'profile_photo',
            'bio', 'current_location', 'current_municipality',
            'current_province', 'preferred_locations', 'skills', 'industries'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+27 XX XXX XXXX'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself, your goals, and what makes you unique...'
            }),
            'current_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 123 Main Street, Sandton'
            }),
            'current_municipality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Johannesburg'
            }),
            'current_province': forms.Select(attrs={
                'class': 'form-select'
            }),
            'preferred_locations': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8'
            }),
            'industries': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['skills'].help_text = 'Hold Ctrl (Cmd on Mac) to select multiple skills'
        self.fields['industries'].help_text = 'Select industries you\'re interested in'
        self.fields['preferred_locations'].help_text = 'Where would you like to work?'


class EmployerProfileForm(forms.ModelForm):
    """Form for employer profile creation and editing"""
    
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'company_logo', 'company_description',
            'company_website', 'contact_person', 'phone',
            'company_location', 'municipality', 'province', 'industries'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your company, what you do, your mission, and culture...'
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+27 XX XXX XXXX'
            }),
            'company_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Address'
            }),
            'municipality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cape Town'
            }),
            'province': forms.Select(attrs={
                'class': 'form-select'
            }),
            'industries': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['industries'].help_text = 'Select all industries your company operates in'


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    
    class Meta:
        model = InternDocument
        fields = ['document_type', 'document', 'description']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional: Add a description for this document'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].help_text = 'Accepted formats: PDF, DOC, DOCX, JPG, PNG'


class EducationForm(forms.ModelForm):
    """Form for adding/editing education records"""
    
    class Meta:
        model = Education
        fields = [
            'institution', 'qualification', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'grade', 'description'
        ]
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'University/College Name'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Science, Diploma'
            }),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science, Business'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Distinction, Pass, GPA 3.5'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about your studies...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        # If currently studying, end_date should be None
        if is_current and end_date:
            cleaned_data['end_date'] = None
        
        # If not current, end_date is required
        if not is_current and not end_date:
            raise forms.ValidationError('End date is required if not currently studying.')
        
        return cleaned_data


class WorkExperienceForm(forms.ModelForm):
    """Form for adding/editing work experience"""
    
    class Meta:
        model = WorkExperience
        fields = [
            'company', 'position', 'start_date', 'end_date',
            'is_current', 'description', 'skills_used'
        ]
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title/Position'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_current': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your responsibilities, achievements, and what you learned...'
            }),
            'skills_used': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '6'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills_used'].help_text = 'Select skills you used in this role'
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        
        # If currently working, end_date should be None
        if is_current and end_date:
            cleaned_data['end_date'] = None
        
        # If not current, end_date is required
        if not is_current and not end_date:
            raise forms.ValidationError('End date is required if not currently working here.')
        
        return cleaned_data


# =====================================================
# INTERNSHIP POSTING FORMS
# =====================================================

from .models import InternshipPost


class InternshipPostForm(forms.ModelForm):
    """Form for creating/editing internship posts"""
    
    class Meta:
        model = InternshipPost
        fields = [
            'title', 'description', 'requirements', 'responsibilities',
            'skills_required', 'industry', 'location', 'municipality',
            'province', 'duration_months', 'stipend', 'start_date',
            'application_deadline', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Development Internship'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the internship opportunity, company culture, and what makes this position unique...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List the qualifications, skills, and experience required...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What will the intern be responsible for? Daily tasks and projects...'
            }),
            'skills_required': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8'
            }),
            'industry': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full address or area'
            }),
            'municipality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Pretoria'
            }),
            'province': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '24',
                'placeholder': 'Duration in months'
            }),
            'stipend': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Monthly stipend (optional)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills_required'].help_text = 'Select all relevant skills'
        self.fields['is_published'].help_text = 'Make this internship visible to interns'
        self.fields['stipend'].help_text = 'Leave blank if unpaid'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        deadline = cleaned_data.get('application_deadline')
        
        from django.utils import timezone
        today = timezone.now().date()
        
        # Application deadline should be in the future
        if deadline and deadline < today:
            raise forms.ValidationError('Application deadline must be in the future.')
        
        # Start date should be after deadline
        if start_date and deadline and start_date <= deadline:
            raise forms.ValidationError('Start date must be after the application deadline.')
        
        return cleaned_data


class InternshipSearchForm(forms.Form):
    """Form for searching and filtering internships"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, company, or description...'
        })
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5'
        })
    )
    industry = forms.ModelChoiceField(
        queryset=Industry.objects.all(),
        required=False,
        empty_label='All Industries',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    province = forms.ChoiceField(
        choices=[('', 'All Provinces')] + [
            ('Eastern Cape', 'Eastern Cape'),
            ('Free State', 'Free State'),
            ('Gauteng', 'Gauteng'),
            ('KwaZulu-Natal', 'KwaZulu-Natal'),
            ('Limpopo', 'Limpopo'),
            ('Mpumalanga', 'Mpumalanga'),
            ('Northern Cape', 'Northern Cape'),
            ('North West', 'North West'),
            ('Western Cape', 'Western Cape'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    stipend_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min stipend',
            'step': '100'
        })
    )
    duration_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max duration (months)'
        })
    )


# =====================================================
# MESSAGING FORMS
# =====================================================

from .models import Message


class MessageForm(forms.ModelForm):
    """Form for sending a message in a conversation"""
    
    class Meta:
        model = Message
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...',
                'required': True
            }),
        }
    
    def clean_message(self):
        """Validate message is not empty"""
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError('Message cannot be empty.')
        if len(message) < 5:
            raise forms.ValidationError('Message must be at least 5 characters long.')
        return message


class StartConversationForm(forms.Form):
    """Form for employers to start a conversation with an intern"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your message to the candidate...',
            'required': True
        }),
        min_length=10,
        help_text='Minimum 10 characters'
    )
    
    def clean_message(self):
        """Validate message"""
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message


# =====================================================
# ADVANCED SEARCH & FILTER FORMS
# =====================================================

class InternFilterForm(forms.Form):
    """Advanced filter form for searching interns (employer use)"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, username, or bio...'
        })
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '6'
        })
    )
    industries = forms.ModelMultipleChoiceField(
        queryset=Industry.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5'
        })
    )
    province = forms.ChoiceField(
        choices=[('', 'All Provinces')] + [
            ('Eastern Cape', 'Eastern Cape'),
            ('Free State', 'Free State'),
            ('Gauteng', 'Gauteng'),
            ('KwaZulu-Natal', 'KwaZulu-Natal'),
            ('Limpopo', 'Limpopo'),
            ('Mpumalanga', 'Mpumalanga'),
            ('Northern Cape', 'Northern Cape'),
            ('North West', 'North West'),
            ('Western Cape', 'Western Cape'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    has_experience = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Has work experience'
    )
    has_education = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Has education records'
    )

