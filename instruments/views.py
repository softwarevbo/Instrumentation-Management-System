from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import engineer_required, admin_required
from .models import Instrument, InstrumentSensor, TelemetryLog
from .forms import InstrumentForm


@login_required
def instrument_list_view(request):
    user = request.user
    if user.is_admin or user.is_engineer:
        instruments = Instrument.objects.select_related('telescope').all().order_by('code')
    elif user.is_observer:
        accessible_telescopes = user.get_accessible_telescopes()
        instruments = Instrument.objects.select_related('telescope').filter(telescope__in=accessible_telescopes).order_by('code')
    else:
        instruments = Instrument.objects.none()
    return render(request, 'instruments/instrument_list.html', {'instruments': instruments})


@login_required
def instrument_detail_view(request, pk):
    instrument = get_object_or_404(Instrument.objects.select_related('telescope'), pk=pk)
    if not request.user.can_access_telescope(instrument.telescope):
        messages.error(request, f"Access Denied: You do not have permission to view instrument '{instrument.code}' on {instrument.telescope.name}.")
        return redirect('instruments:instrument_list')

    sensors = instrument.sensors.all()
    telemetry = instrument.telemetry_logs.all()[:30]
    return render(request, 'instruments/instrument_detail.html', {
        'instrument': instrument,
        'sensors': sensors,
        'telemetry': telemetry,
    })


@login_required
@admin_required
def instrument_create_view(request):
    if request.method == 'POST':
        form = InstrumentForm(request.POST)
        if form.is_valid():
            inst = form.save()
            messages.success(request, f"Instrument '{inst.name}' registered in system.")
            return redirect('instruments:instrument_detail', pk=inst.pk)
    else:
        form = InstrumentForm()
    return render(request, 'instruments/instrument_form.html', {'form': form, 'action': 'Register New Instrument'})


@login_required
@engineer_required
def instrument_edit_view(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    if request.method == 'POST':
        form = InstrumentForm(request.POST, instance=instrument)
        if form.is_valid():
            instrument = form.save()
            messages.success(request, f"Instrument {instrument.code} settings updated.")
            return redirect('instruments:instrument_detail', pk=instrument.pk)
    else:
        form = InstrumentForm(instance=instrument)
    return render(request, 'instruments/instrument_form.html', {'form': form, 'action': f'Edit {instrument.code}'})


@login_required
@engineer_required
def update_status_view(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Instrument.STATUS_CHOICES]
        if new_status in valid_statuses:
            instrument.status = new_status
            instrument.save()
            TelemetryLog.objects.create(
                instrument=instrument,
                sensor_name='Status Change',
                value=0,
                unit='event',
                status_flag='normal'
            )
            messages.success(request, f"Instrument {instrument.code} status set to {instrument.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selection.")
    return redirect('instruments:instrument_detail', pk=pk)
