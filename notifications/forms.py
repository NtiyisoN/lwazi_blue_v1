from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """Form for managing notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_application_submitted',
            'email_application_status',
            'email_new_message',
            'email_matched_internships',
            'email_deadline_reminders',
            'internal_notifications',
        ]
        widgets = {
            'email_application_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_application_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_new_message': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_matched_internships': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_deadline_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'internal_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

