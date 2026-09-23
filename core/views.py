from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from telescopes.models import Telescope
from instruments.models import Instrument
from maintenance.models import MaintenanceTicket, CalibrationLog
from accounts.models import User
from .models import SiteFeedback
from .forms import SiteFeedbackForm


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


def feedback_view(request):
    """
    Feedback submission & showcase view accessible to all users.
    """
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '').strip()

    if request.method == 'POST':
        form = SiteFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
                if not feedback.name:
                    feedback.name = request.user.get_full_name() or request.user.username
                if not feedback.email:
                    feedback.email = request.user.email
            feedback.save()
            messages.success(request, "Thank you! Your feedback/bug report has been submitted successfully.")
            return redirect('core:feedback')
        else:
            messages.error(request, "Please correct the errors in the feedback form.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
        form = SiteFeedbackForm(initial=initial_data)

    feedbacks = SiteFeedback.objects.all()

    # Hide unapproved or private non-user feedback unless staff/admin
    if not (request.user.is_authenticated and request.user.is_admin):
        feedbacks = feedbacks.filter(is_public=True)

    if category_filter:
        feedbacks = feedbacks.filter(category=category_filter)
    if status_filter:
        feedbacks = feedbacks.filter(status=status_filter)
    if search_query:
        feedbacks = feedbacks.filter(
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    # Statistics by Category
    total_count = SiteFeedback.objects.count()
    bug_count = SiteFeedback.objects.filter(category='bug_error').count()
    ui_count = SiteFeedback.objects.filter(category='ui_ux').count()
    feature_count = SiteFeedback.objects.filter(category='feature_req').count()
    hardware_count = SiteFeedback.objects.filter(category='hardware_error').count()
    open_count = SiteFeedback.objects.filter(status__in=['new', 'under_review']).count()

    categories = SiteFeedback.CATEGORY_CHOICES

    context = {
        'form': form,
        'feedbacks': feedbacks,
        'total_count': total_count,
        'bug_count': bug_count,
        'ui_count': ui_count,
        'feature_count': feature_count,
        'hardware_count': hardware_count,
        'open_count': open_count,
        'selected_category': category_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'categories': categories,
    }

    return render(request, 'core/feedback.html', context)



@login_required
def feedback_respond_view(request, pk):
    """
    Allows admin/staff to respond to feedback or change its status.
    """
    if not request.user.is_admin:
        messages.error(request, "Access denied: Only system administrators can respond to feedback.")
        return redirect('core:feedback')

    feedback = get_object_or_404(SiteFeedback, pk=pk)

    if request.method == 'POST':
        response_text = request.POST.get('admin_response', '').strip()
        new_status = request.POST.get('status', feedback.status)
        
        feedback.admin_response = response_text
        feedback.status = new_status
        feedback.save()

        messages.success(request, f"Updated feedback response for '{feedback.subject}'.")

    return redirect('core:feedback')


@login_required
def mark_notifications_read(request):
    """
    Sets user.last_notif_viewed = now() so the notification bell
    count drops to 0. Called via AJAX GET from the bell icon.
    """
    request.user.last_notif_viewed = timezone.now()
    request.user.save(update_fields=['last_notif_viewed'])
    return JsonResponse({'status': 'ok'})
