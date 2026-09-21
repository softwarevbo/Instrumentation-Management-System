from django import forms
from .models import Instrument


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = [
            'name', 'code', 'instrument_type', 'telescope', 'status',
            'detector_temp', 'setpoint_temp', 'vacuum_pressure', 'cooling_power_percent',
            'gain', 'binning', 'readout_speed', 'active_filter'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'instrument_type': forms.Select(attrs={'class': 'form-select'}),
            'telescope': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'detector_temp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'setpoint_temp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'vacuum_pressure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'}),
            'cooling_power_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'gain': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'binning': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1x1'}),
            'readout_speed': forms.TextInput(attrs={'class': 'form-control'}),
            'active_filter': forms.TextInput(attrs={'class': 'form-control'}),
        }
