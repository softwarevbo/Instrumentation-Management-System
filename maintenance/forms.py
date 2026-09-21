from django import forms
from accounts.models import User
from .models import MaintenanceTicket, CalibrationLog


class MaintenanceTicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_engineer'].queryset = User.objects.filter(role__in=['admin', 'engineer'])

    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'severity', 'instrument', 'telescope', 'assigned_engineer']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'instrument': forms.Select(attrs={'class': 'form-select'}),
            'telescope': forms.Select(attrs={'class': 'form-select'}),
            'assigned_engineer': forms.Select(attrs={'class': 'form-select'}),
        }


class ResolveTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['status', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class CalibrationLogForm(forms.ModelForm):
    class Meta:
        model = CalibrationLog
        fields = ['instrument', 'calibration_type', 'standard_lamp_or_target', 'status', 'notes']
        widgets = {
            'instrument': forms.Select(attrs={'class': 'form-select'}),
            'calibration_type': forms.Select(attrs={'class': 'form-select'}),
            'standard_lamp_or_target': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
