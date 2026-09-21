from django import forms
from .models import ObservationTarget


class ObservationTargetForm(forms.ModelForm):
    class Meta:
        model = ObservationTarget
        fields = ['name', 'catalog_id', 'right_ascension', 'declination', 'object_class', 'magnitude', 'distance_ly', 'observation_date', 'recommended_filter', 'epoch', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'catalog_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NGC 224 / HD 209458'}),
            'right_ascension': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00h 42m 44.3s'}),
            'declination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+41° 16\' 09\"'}),
            'object_class': forms.Select(attrs={'class': 'form-select'}),
            'magnitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'distance_ly': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'observation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'recommended_filter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'V (550nm) / H-alpha / Iodine Cell'}),
            'epoch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'J2000.0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
