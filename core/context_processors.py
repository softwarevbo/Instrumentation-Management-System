from telescopes.models import Telescope
from instruments.models import Instrument
from maintenance.models import MaintenanceTicket
from django.utils import timezone


def observatory_context(request):
    """
    Global context processor: injects observatory-wide summary data
    into every template for the sidebar, topbar, and notification bell.
    """
    context = {}
    if request.user.is_authenticated:
        context['total_telescopes'] = Telescope.objects.count()
        context['online_telescopes'] = Telescope.objects.filter(status='online').count()
        context['total_instruments'] = Instrument.objects.count()
        context['online_instruments'] = Instrument.objects.filter(status='online').count()
        context['open_tickets'] = MaintenanceTicket.objects.filter(status='open').count()
        context['critical_tickets'] = MaintenanceTicket.objects.filter(status='open', severity='critical').count()

        # ── NOTIFICATION COUNT ────────────────────────────────────────────
        # Count new discussions and feedback posted AFTER the user last
        # viewed notifications. If never viewed, count everything.
        from telescopes.models import TelescopeDiscussion
        from core.models import SiteFeedback

        last_viewed = request.user.last_notif_viewed

        if last_viewed:
            new_discussions = TelescopeDiscussion.objects.filter(
                created_at__gt=last_viewed
            ).exclude(user=request.user).count()

            new_feedback = SiteFeedback.objects.filter(
                created_at__gt=last_viewed
            ).exclude(user=request.user).count()
        else:
            # First time: count everything not posted by this user
            new_discussions = TelescopeDiscussion.objects.exclude(
                user=request.user
            ).count()
            new_feedback = SiteFeedback.objects.exclude(
                user=request.user
            ).count()

        context['notif_count'] = new_discussions + new_feedback
        context['notif_discussions'] = new_discussions
        context['notif_feedback'] = new_feedback

    return context
