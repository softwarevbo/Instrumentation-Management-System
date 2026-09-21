from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserProfileForm, CustomUserCreationForm
from .decorators import admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.display_name}!")
            next_url = request.GET.get('next') or 'core:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile settings have been updated.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'user_obj': request.user})


@login_required
@admin_required
def user_list_view(request):
    from django.db import models

    role = request.GET.get('role', '').strip()
    department = request.GET.get('department', '').strip()
    q = request.GET.get('q', '').strip()

    users = User.objects.all()

    if role:
        users = users.filter(role=role)
    if department:
        users = users.filter(department=department)
    if q:
        users = users.filter(
            models.Q(username__icontains=q) |
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(designation__icontains=q)
        )

    users = users.order_by('role', '-date_joined')

    # Category Statistics Counts
    total_users_count = User.objects.count()
    admin_users_count = User.objects.filter(role='admin').count()
    engineer_users_count = User.objects.filter(role='engineer').count()
    observer_users_count = User.objects.filter(role='observer').count()

    # Categorized user lists
    admin_users = users.filter(role='admin')
    engineer_users = users.filter(role='engineer')
    observer_users = users.filter(role='observer')

    context = {
        'users': users,
        'admin_users': admin_users,
        'engineer_users': engineer_users,
        'observer_users': observer_users,
        'selected_role': role,
        'selected_department': department,
        'q': q,
        'total_users_count': total_users_count,
        'admin_users_count': admin_users_count,
        'engineer_users_count': engineer_users_count,
        'observer_users_count': observer_users_count,
        'department_choices': User.DEPARTMENT_CHOICES,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@admin_required
def user_create_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User account '{user.username}' ({user.get_role_display()}) created successfully.")
            return redirect('accounts:user_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Create New User'})


@login_required
@admin_required
def user_edit_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    from .forms import AdminUserEditForm

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            user = form.save(commit=False)
            new_pwd = form.cleaned_data.get('new_password')
            if new_pwd:
                user.set_password(new_pwd)
            user.save()
            form.save_m2m()
            messages.success(request, f"User account '{user.username}' updated successfully.")
            return redirect('accounts:user_list')
        else:
            messages.error(request, "Failed to update user account. Please check the form errors below.")
    else:
        form = AdminUserEditForm(instance=target_user)

    return render(request, 'accounts/user_edit.html', {'form': form, 'target_user': target_user})


@login_required
@admin_required
def user_delete_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if request.user.pk == target_user.pk:
            messages.error(request, "You cannot delete your own active administrator account!")
            return redirect('accounts:user_list')

        username = target_user.username
        target_user.delete()
        messages.success(request, f"User account '{username}' deleted successfully.")
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {'target_user': target_user})


@login_required
def toggle_theme_view(request):
    if request.user.is_authenticated:
        request.user.theme_preference = 'light' if request.user.theme_preference == 'dark' else 'dark'
        request.user.save()
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))
