from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import engineer_required, admin_required
from .models import Telescope, TelescopeLog
from .forms import TelescopeForm, SlewTargetForm


@login_required
def telescope_list_view(request):
    telescopes = request.user.get_accessible_telescopes().order_by('code')
    return render(request, 'telescopes/telescope_list.html', {'telescopes': telescopes})


@login_required
def telescope_detail_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, f"Access Denied: You are not authorized to view or control telescope [{telescope.code}].")
        return redirect('telescopes:telescope_list')

    from observations.models import ObservationTarget
    targets = ObservationTarget.objects.all().order_by('name')

    slew_form = SlewTargetForm(initial={
        'right_ascension': telescope.right_ascension,
        'declination': telescope.declination,
        'epoch': telescope.epoch,
    })
    logs = telescope.logs.all()[:20]
    instruments = telescope.instruments.all()
    return render(request, 'telescopes/telescope_detail.html', {
        'telescope': telescope,
        'targets': targets,
        'slew_form': slew_form,
        'logs': logs,
        'instruments': instruments,
    })


@login_required
@admin_required
def telescope_create_view(request):
    if request.method == 'POST':
        form = TelescopeForm(request.POST)
        if form.is_valid():
            telescope = form.save()
            messages.success(request, f"Telescope '{telescope.name}' added to observatory database.")
            return redirect('telescopes:telescope_detail', pk=telescope.pk)
    else:
        form = TelescopeForm()
    return render(request, 'telescopes/telescope_form.html', {'form': form, 'action': 'Add New Telescope'})


@login_required
def telescope_edit_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, "Access Denied: You are not authorized to modify this telescope.")
        return redirect('telescopes:telescope_list')

    if request.method == 'POST':
        form = TelescopeForm(request.POST, instance=telescope)
        if form.is_valid():
            telescope = form.save()
            messages.success(request, f"Telescope settings for {telescope.code} updated.")
            return redirect('telescopes:telescope_detail', pk=telescope.pk)
    else:
        form = TelescopeForm(instance=telescope)
    return render(request, 'telescopes/telescope_form.html', {'form': form, 'action': f'Edit {telescope.code}'})


@login_required
def slew_telescope_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, "Access Denied: You are not authorized to slew this telescope.")
        return redirect('telescopes:telescope_list')

    if request.method == 'POST':
        form = SlewTargetForm(request.POST)
        if form.is_valid():
            target_name = form.cleaned_data.get('target_name') or 'Custom Coordinates'
            ra = form.cleaned_data.get('right_ascension')
            dec = form.cleaned_data.get('declination')
            epoch = form.cleaned_data.get('epoch')

            telescope.right_ascension = ra
            telescope.declination = dec
            telescope.epoch = epoch
            telescope.status = Telescope.STATUS_TRACKING
            telescope.save()

            TelescopeLog.objects.create(
                telescope=telescope,
                user=request.user,
                event_type='slew',
                message=f"Slewed and locked tracking on target '{target_name}' at RA: {ra}, DEC: {dec} ({epoch})."
            )
            messages.success(request, f"Telescope {telescope.code} slewed to {target_name} ({ra}, {dec}). Tracking active.")
    return redirect('telescopes:telescope_detail', pk=telescope.pk)


@login_required
def toggle_dome_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, "Access Denied: You are not authorized to control the dome for this telescope.")
        return redirect('telescopes:telescope_list')

    if telescope.dome_status == 'open':
        telescope.dome_status = 'closed'
        event_type = 'dome_close'
        msg = "Dome shutter closed."
    else:
        telescope.dome_status = 'open'
        event_type = 'dome_open'
        msg = "Dome shutter opened for observation."

    telescope.save()
    TelescopeLog.objects.create(
        telescope=telescope,
        user=request.user,
        event_type=event_type,
        message=msg
    )
    messages.info(request, f"Dome state for {telescope.code} updated to {telescope.get_dome_status_display()}.")
    return redirect('telescopes:telescope_detail', pk=telescope.pk)


@login_required
def update_telemetry_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, "Access Denied: You are not authorized to modify parameters for this telescope.")
        return redirect('telescopes:telescope_list')

    if request.method == 'POST':
        focus_pos = request.POST.get('focus_position')
        mirror_temp = request.POST.get('primary_mirror_temp')
        humidity = request.POST.get('humidity')
        ra = request.POST.get('right_ascension')
        dec = request.POST.get('declination')
        epoch = request.POST.get('epoch')

        changes = []
        if focus_pos:
            try:
                telescope.focus_position = float(focus_pos)
                changes.append(f"Focus={telescope.focus_position}mm")
            except ValueError:
                pass
        if mirror_temp:
            try:
                telescope.primary_mirror_temp = float(mirror_temp)
                changes.append(f"Mirror Temp={telescope.primary_mirror_temp}°C")
            except ValueError:
                pass
        if humidity:
            try:
                telescope.humidity = float(humidity)
                changes.append(f"Humidity={telescope.humidity}%")
            except ValueError:
                pass
        if ra and ra.strip():
            telescope.right_ascension = ra.strip()
            changes.append(f"RA={telescope.right_ascension}")
        if dec and dec.strip():
            telescope.declination = dec.strip()
            changes.append(f"DEC={telescope.declination}")
        if epoch and epoch.strip():
            telescope.epoch = epoch.strip()

        telescope.save()

        if changes:
            TelescopeLog.objects.create(
                telescope=telescope,
                user=request.user,
                event_type='telemetry_update',
                message=f"Updated parameters: {', '.join(changes)}"
            )
            messages.success(request, f"Telescope {telescope.code} parameters updated: {', '.join(changes)}.")
        else:
            messages.info(request, "No parameter changes submitted.")

    return redirect('telescopes:telescope_detail', pk=pk)

