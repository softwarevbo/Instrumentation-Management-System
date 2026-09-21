from django import forms
from .models import Telescope


class TelescopeForm(forms.ModelForm):
    class Meta:
        model = Telescope
        fields = ['name', 'code', 'aperture', 'focal_ratio', 'mount_type', 'location', 'status', 'dome_status', 'focus_position']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'aperture': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'focal_ratio': forms.TextInput(attrs={'class': 'form-control'}),
            'mount_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'dome_status': forms.Select(attrs={'class': 'form-select'}),
            'focus_position': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SlewTargetForm(forms.Form):
    target_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M31 / NGC 224'}))
    right_ascension = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12h 30m 45.2s'}))
    declination = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+45° 15\' 22.0"' }))
    epoch = forms.CharField(max_length=10, initial="J2000", widget=forms.TextInput(attrs={'class': 'form-control'}))
