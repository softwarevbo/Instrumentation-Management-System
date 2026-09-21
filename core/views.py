from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from telescopes.models import Telescope
from instruments.models import Instrument
from maintenance.models import MaintenanceTicket, CalibrationLog
from accounts.models import User


@login_required
def dashboard_view(request):
    user = request.user

    # Shared summary counts
    telescopes = user.get_accessible_telescopes()
    instruments = Instrument.objects.select_related('telescope').all()
    open_tickets = MaintenanceTicket.objects.filter(status='open').count()
    critical_tickets = MaintenanceTicket.objects.filter(status='open', severity='critical').count()

    # Counts by status
    telescope_status = {
        'online': telescopes.filter(status='online').count(),
        'tracking': telescopes.filter(status='tracking').count(),
        'maintenance': telescopes.filter(status='maintenance').count(),
        'fault': telescopes.filter(status='fault').count(),
        'idle': telescopes.filter(status='idle').count(),
    }
    instrument_status = {
        'online': instruments.filter(status='online').count(),
        'calibrating': instruments.filter(status='calibrating').count(),
        'maintenance': instruments.filter(status='maintenance').count(),
        'error': instruments.filter(status='error').count(),
        'standby': instruments.filter(status='standby').count(),
    }

    context = {
        'telescopes': telescopes,
        'instruments': instruments,
        'open_tickets': open_tickets,
        'critical_tickets': critical_tickets,
        'telescope_status': telescope_status,
        'instrument_status': instrument_status,
        'total_users': User.objects.count() if user.is_admin else None,
        'my_tickets': MaintenanceTicket.objects.filter(assigned_engineer=user, status__in=['open', 'in_progress']).count() if user.is_engineer else 0,
        'recent_calibrations': CalibrationLog.objects.select_related('instrument', 'engineer').all()[:5],
        'recent_tickets': MaintenanceTicket.objects.select_related('instrument', 'telescope', 'assigned_engineer').filter(status__in=['open', 'in_progress'])[:5],
    }

    return render(request, 'core/dashboard.html', context)
