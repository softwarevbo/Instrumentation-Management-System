from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from accounts.decorators import engineer_required, admin_required
from .models import Telescope, TelescopeLog, TelescopeDiscussion, TelescopeDiscussionReply
from .forms import TelescopeForm, SlewTargetForm, TelescopeDiscussionForm, TelescopeDiscussionReplyForm


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
    discussions = telescope.discussions.select_related('user').annotate(reply_count=Count('replies')).order_by('-is_pinned', '-created_at')

    # Discussion quick post form preset to this telescope
    discussion_form = TelescopeDiscussionForm(initial={'telescope': telescope})

    return render(request, 'telescopes/telescope_detail.html', {
        'telescope': telescope,
        'targets': targets,
        'slew_form': slew_form,
        'logs': logs,
        'instruments': instruments,
        'discussions': discussions,
        'discussion_form': discussion_form,
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
def stop_telescope_view(request, pk):
    telescope = get_object_or_404(Telescope, pk=pk)
    if not request.user.can_access_telescope(telescope):
        messages.error(request, "Access Denied: You are not authorized to stop this telescope.")
        return redirect('telescopes:telescope_list')

    if request.method == 'POST':
        telescope.status = Telescope.STATUS_IDLE
        telescope.save()

        TelescopeLog.objects.create(
            telescope=telescope,
            user=request.user,
            event_type='stop',
            message="HALT MOTION: Mount motion stopped and tracking halted."
        )
        messages.warning(request, f"Telescope {telescope.code}: Motion halted. Tracking disengaged.")
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


# ══════════════════════════════════════════════════════════════════════════════
# TELESCOPE DISCUSSIONS VIEWS (SEPARATE DISCUSSIONS FOR ALL TELESCOPES)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def discussion_hub_view(request):
    """
    Centralized Discussion Hub showing discussions for all separate telescopes.
    Supports filtering by telescope, topic category, date range, and search query.
    """
    telescopes = request.user.get_accessible_telescopes()
    selected_telescope_id = request.GET.get('telescope', '')
    selected_category = request.GET.get('category', '')
    search_query = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    discussions = TelescopeDiscussion.objects.filter(telescope__in=telescopes).select_related('telescope', 'user').annotate(reply_count=Count('replies'))

    selected_telescope = None
    if selected_telescope_id:
        try:
            selected_telescope = telescopes.get(pk=selected_telescope_id)
            discussions = discussions.filter(telescope=selected_telescope)
        except (Telescope.DoesNotExist, ValueError):
            pass

    if selected_category:
        discussions = discussions.filter(category=selected_category)

    if search_query:
        discussions = discussions.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(telescope__code__icontains=search_query)
        )

    # ── DATE FILTERS ───────────────────────────────────────────────────────
    if date_from:
        try:
            discussions = discussions.filter(created_at__date__gte=date_from)
        except Exception:
            date_from = ''
    if date_to:
        try:
            discussions = discussions.filter(created_at__date__lte=date_to)
        except Exception:
            date_to = ''

    discussions = discussions.order_by('-is_pinned', '-created_at')

    # Initial form data
    initial_form = {}
    if selected_telescope:
        initial_form['telescope'] = selected_telescope
    form = TelescopeDiscussionForm(initial=initial_form)
    form.fields['telescope'].queryset = telescopes

    context = {
        'discussions': discussions,
        'telescopes': telescopes,
        'selected_telescope': selected_telescope,
        'selected_category': selected_category,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'categories': TelescopeDiscussion.CATEGORY_CHOICES,
        'form': form,
    }

    return render(request, 'telescopes/discussion_hub.html', context)



@login_required
def discussion_detail_view(request, pk):
    """
    Detailed discussion post page with full thread and reply box.
    """
    discussion = get_object_or_404(TelescopeDiscussion.objects.select_related('telescope', 'user'), pk=pk)
    if not request.user.can_access_telescope(discussion.telescope):
        messages.error(request, "Access Denied: You do not have permission to view discussions for this telescope.")
        return redirect('telescopes:discussion_hub')

    replies = discussion.replies.select_related('user').order_by('created_at')

    if request.method == 'POST':
        reply_form = TelescopeDiscussionReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.discussion = discussion
            reply.user = request.user
            reply.save()
            messages.success(request, "Reply posted successfully.")
            return redirect('telescopes:discussion_detail', pk=discussion.pk)
    else:
        reply_form = TelescopeDiscussionReplyForm()

    return render(request, 'telescopes/discussion_detail.html', {
        'discussion': discussion,
        'replies': replies,
        'reply_form': reply_form,
    })


@login_required
def discussion_create_view(request):
    """
    Handles submission of new discussion topics.
    """
    if request.method == 'POST':
        form = TelescopeDiscussionForm(request.POST)
        # Check telescope access
        telescope_id = request.POST.get('telescope')
        if telescope_id:
            try:
                telescope = Telescope.objects.get(pk=telescope_id)
                if not request.user.can_access_telescope(telescope):
                    messages.error(request, "Access Denied: You cannot post discussions for this telescope.")
                    return redirect('telescopes:discussion_hub')
            except Telescope.DoesNotExist:
                pass

        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.user = request.user
            discussion.save()
            messages.success(request, f"Discussion '{discussion.title}' published for telescope [{discussion.telescope.code}].")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('telescopes:discussion_detail', pk=discussion.pk)
        else:
            messages.error(request, "Failed to create discussion. Please check the form errors.")

    return redirect('telescopes:discussion_hub')


@login_required
def toggle_pin_discussion_view(request, pk):
    """
    Allows engineers or admins to pin/unpin a discussion topic.
    """
    discussion = get_object_or_404(TelescopeDiscussion, pk=pk)
    if not (request.user.is_admin or request.user.is_engineer):
        messages.error(request, "Access Denied: Only engineers and admins can pin discussions.")
        return redirect('telescopes:discussion_detail', pk=pk)

    discussion.is_pinned = not discussion.is_pinned
    discussion.save()

    status_str = "pinned to top" if discussion.is_pinned else "unpinned"
    messages.info(request, f"Discussion '{discussion.title}' has been {status_str}.")
    return redirect('telescopes:discussion_detail', pk=pk)


