from django import forms
from .models import Application
from core.models import InternDocument


class ApplicationForm(forms.ModelForm):
    """Form for submitting an application"""
    
    class Meta:
        model = Application
        fields = ['cover_letter', 'additional_documents']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write a compelling cover letter explaining why you are interested in this internship and why you would be a great fit...'
            }),
            'additional_documents': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, intern_profile=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter documents to show only the intern's latest documents
        if intern_profile:
            self.fields['additional_documents'].queryset = InternDocument.objects.filter(
                intern=intern_profile,
                is_latest=True
            )
        
        self.fields['cover_letter'].help_text = 'Minimum 100 characters'
        self.fields['additional_documents'].help_text = 'Select any additional documents to include'
        self.fields['additional_documents'].required = False
    
    def clean_cover_letter(self):
        """Validate cover letter length"""
        cover_letter = self.cleaned_data.get('cover_letter', '')
        if len(cover_letter.strip()) < 100:
            raise forms.ValidationError('Cover letter must be at least 100 characters long.')
        return cover_letter


class ApplicationStatusForm(forms.ModelForm):
    """Form for employers to update application status"""
    
    class Meta:
        model = Application
        fields = ['status', 'employer_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'employer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add internal notes about this application (not visible to the applicant)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].help_text = 'Update the application status'
        self.fields['employer_notes'].help_text = 'Internal notes (not visible to applicant)'
        self.fields['employer_notes'].required = False

