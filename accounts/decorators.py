from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles=None):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Permission Denied: Your account role does not have access to this resource.")
            raise PermissionDenied
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(['admin'])(view_func)


def engineer_required(view_func):
    return role_required(['admin', 'engineer'])(view_func)


def observer_required(view_func):
    return role_required(['admin', 'engineer', 'observer'])(view_func)
