from django import forms
from .models import SiteFeedback


class SiteFeedbackForm(forms.ModelForm):
    class Meta:
        model = SiteFeedback
        fields = ['category', 'subject', 'message', 'name', 'email', 'is_public']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title of bug, issue, or feedback'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the bug, error details, steps to reproduce, or feedback...'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name (optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Contact Email (optional)'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

