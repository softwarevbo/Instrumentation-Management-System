from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import engineer_required, admin_required
from .models import MaintenanceTicket, CalibrationLog
from .forms import MaintenanceTicketForm, ResolveTicketForm, CalibrationLogForm


@login_required
def ticket_list_view(request):
    from django.db import models

    tickets = MaintenanceTicket.objects.select_related('instrument', 'telescope', 'assigned_engineer', 'reported_by').all()

    # Search & Filters
    q = request.GET.get('q', '').strip()
    severity = request.GET.get('severity', '').strip()
    status = request.GET.get('status', '').strip()
    telescope_id = request.GET.get('telescope', '').strip()
    instrument_id = request.GET.get('instrument', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if q:
        tickets = tickets.filter(
            models.Q(title__icontains=q) |
            models.Q(description__icontains=q) |
            models.Q(resolution_notes__icontains=q)
        )
    if severity:
        tickets = tickets.filter(severity=severity)
    if status:
        tickets = tickets.filter(status=status)
    if telescope_id:
        tickets = tickets.filter(telescope_id=telescope_id)
    if instrument_id:
        tickets = tickets.filter(instrument_id=instrument_id)
    if date_from:
        tickets = tickets.filter(created_at__date__gte=date_from)
    if date_to:
        tickets = tickets.filter(created_at__date__lte=date_to)

    open_count = MaintenanceTicket.objects.filter(status='open').count()
    in_progress_count = MaintenanceTicket.objects.filter(status='in_progress').count()
    resolved_count = MaintenanceTicket.objects.filter(status__in=['resolved', 'closed']).count()

    from telescopes.models import Telescope
    from instruments.models import Instrument

    telescopes = Telescope.objects.all()
    instruments = Instrument.objects.all()

    return render(request, 'maintenance/ticket_list.html', {
        'tickets': tickets,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'q': q,
        'selected_severity': severity,
        'selected_status': status,
        'selected_telescope': telescope_id,
        'selected_instrument': instrument_id,
        'date_from': date_from,
        'date_to': date_to,
        'severity_choices': MaintenanceTicket.SEVERITY_CHOICES,
        'status_choices': MaintenanceTicket.STATUS_CHOICES,
        'telescopes': telescopes,
        'instruments': instruments,
    })


@login_required
def ticket_detail_view(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)
    resolve_form = ResolveTicketForm(instance=ticket)
    return render(request, 'maintenance/ticket_detail.html', {
        'ticket': ticket,
        'resolve_form': resolve_form,
    })


@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        form = MaintenanceTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.reported_by = request.user
            ticket.save()
            messages.success(request, f"Maintenance ticket '{ticket.title}' created successfully.")
            return redirect('maintenance:ticket_detail', pk=ticket.pk)
    else:
        form = MaintenanceTicketForm()
    return render(request, 'maintenance/ticket_form.html', {'form': form, 'action': 'Create Maintenance Ticket'})


@login_required
@engineer_required
def ticket_resolve_view(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)
    if request.method == 'POST':
        form = ResolveTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            if ticket.status == 'resolved':
                ticket.resolved_at = timezone.now()
            ticket.save()
            messages.success(request, f"Ticket '{ticket.title}' updated to {ticket.get_status_display()}.")
    return redirect('maintenance:ticket_detail', pk=pk)


@login_required
def calibration_list_view(request):
    user = request.user
    if user.is_admin or user.is_engineer:
        cals = CalibrationLog.objects.select_related('instrument', 'instrument__telescope', 'engineer').all()
    elif user.is_observer:
        accessible_telescopes = user.get_accessible_telescopes()
        cals = CalibrationLog.objects.select_related('instrument', 'instrument__telescope', 'engineer').filter(
            instrument__telescope__in=accessible_telescopes
        )
    else:
        cals = CalibrationLog.objects.none()

    return render(request, 'maintenance/calibration_list.html', {
        'calibrations': cals,
        'status_choices': CalibrationLog.CAL_STATUS_CHOICES,
    })


@login_required
def calibration_status_update_view(request, pk):
    cal = get_object_or_404(CalibrationLog.objects.select_related('instrument__telescope'), pk=pk)
    if not request.user.can_access_telescope(cal.instrument.telescope):
        messages.error(request, "Access Denied: You do not have permission to update calibrations for this telescope.")
        return redirect('maintenance:calibration_list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in CalibrationLog.CAL_STATUS_CHOICES]
        if new_status in valid_statuses:
            cal.status = new_status
            cal.save()
            messages.success(request, f"Calibration run #{cal.pk} status updated to '{cal.get_status_display()}'.")
        else:
            messages.error(request, "Invalid calibration status selection.")
    return redirect('maintenance:calibration_list')


@login_required
@engineer_required
def calibration_create_view(request):
    if request.method == 'POST':
        form = CalibrationLogForm(request.POST)
        if form.is_valid():
            cal = form.save(commit=False)
            cal.engineer = request.user
            cal.save()
            messages.success(request, f"Calibration run '{cal.get_calibration_type_display()}' logged for {cal.instrument.code}.")
            return redirect('maintenance:calibration_list')
    else:
        form = CalibrationLogForm()
    return render(request, 'maintenance/calibration_form.html', {'form': form, 'action': 'Log Calibration Run'})

