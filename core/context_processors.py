from telescopes.models import Telescope
from instruments.models import Instrument
from maintenance.models import MaintenanceTicket


def observatory_context(request):
    """
    Global context processor: injects observatory-wide summary data
    into every template for the sidebar and topbar.
    """
    context = {}
    if request.user.is_authenticated:
        context['total_telescopes'] = Telescope.objects.count()
        context['online_telescopes'] = Telescope.objects.filter(status='online').count()
        context['total_instruments'] = Instrument.objects.count()
        context['online_instruments'] = Instrument.objects.filter(status='online').count()
        context['open_tickets'] = MaintenanceTicket.objects.filter(status='open').count()
        context['critical_tickets'] = MaintenanceTicket.objects.filter(status='open', severity='critical').count()
    return context
