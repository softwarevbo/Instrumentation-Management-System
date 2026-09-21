from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import ObservationTarget
from .forms import ObservationTargetForm


@login_required
def target_list_view(request):
    targets = ObservationTarget.objects.all()

    # Search & Filters
    q = request.GET.get('q', '').strip()
    object_class = request.GET.get('object_class', '').strip()
    filter_name = request.GET.get('filter_name', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if q:
        targets = targets.filter(models.Q(name__icontains=q) | models.Q(catalog_id__icontains=q) | models.Q(notes__icontains=q))
    if object_class:
        targets = targets.filter(object_class=object_class)
    if filter_name:
        targets = targets.filter(recommended_filter__icontains=filter_name)
    if date_from:
        targets = targets.filter(observation_date__gte=date_from)
    if date_to:
        targets = targets.filter(observation_date__lte=date_to)

    targets = targets.order_by('-observation_date', 'name')

    # Get distinct filters for dropdown
    available_filters = (
        ObservationTarget.objects.exclude(recommended_filter='')
        .values_list('recommended_filter', flat=True)
        .distinct()
    )

    context = {
        'targets': targets,
        'q': q,
        'selected_object_class': object_class,
        'selected_filter': filter_name,
        'date_from': date_from,
        'date_to': date_to,
        'object_choices': ObservationTarget.OBJECT_CHOICES,
        'available_filters': available_filters,
    }
    return render(request, 'observations/target_list.html', context)


@login_required
def target_create_view(request):
    if request.method == 'POST':
        form = ObservationTargetForm(request.POST)
        if form.is_valid():
            target = form.save()
            messages.success(request, f"Target '{target.name}' added to catalog successfully.")
            return redirect('observations:target_list')
        else:
            messages.error(request, "Failed to save target. Please correct the highlighted errors below.")
    else:
        form = ObservationTargetForm()
    return render(request, 'observations/target_form.html', {'form': form, 'action': 'Add Target to Catalog'})


@login_required
def target_edit_view(request, pk):
    target = get_object_or_404(ObservationTarget, pk=pk)
    if request.method == 'POST':
        form = ObservationTargetForm(request.POST, instance=target)
        if form.is_valid():
            target = form.save()
            messages.success(request, f"Target '{target.name}' updated successfully.")
            return redirect('observations:target_list')
        else:
            messages.error(request, "Failed to update target. Please correct the highlighted errors below.")
    else:
        form = ObservationTargetForm(instance=target)
    return render(request, 'observations/target_form.html', {'form': form, 'action': f'Edit Target: {target.name}', 'target': target})


@login_required
def target_delete_view(request, pk):
    target = get_object_or_404(ObservationTarget, pk=pk)
    if request.method == 'POST':
        name = target.name
        target.delete()
        messages.success(request, f"Target '{name}' deleted from catalog.")
        return redirect('observations:target_list')
    return redirect('observations:target_list')
