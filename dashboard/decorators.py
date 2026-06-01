"""
Access-control decorators for the Unity Battalion dashboards.

Usage:
    from dashboard.decorators import super_admin_required, company_admin_required

    @super_admin_required
    def my_view(request):
        ...
"""

from functools import wraps

from django.shortcuts import redirect


def super_admin_required(view_func):
    """
    Protects a view so that only authenticated super-admin users can
    access it.

    Unauthenticated visitors are sent to the hidden super-admin login
    portal (/battalion-control/).  Authenticated users who lack the
    super_admin role (e.g. a company_admin who somehow guessed the URL)
    are also redirected there.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/battalion-control/')
        if not request.user.is_super_admin:
            return redirect('/battalion-control/')
        return view_func(request, *args, **kwargs)
    return wrapper


def company_admin_required(view_func):
    """
    Protects a view so that only authenticated company-admin users can
    access it.

    Unauthenticated visitors are sent to the regular login page.
    Authenticated super-admins are allowed through as well, because
    super-admins should be able to view everything a company-admin sees
    (they are a superset of permissions).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        # Super admins can access company-admin views too
        if not (request.user.is_company_admin or request.user.is_super_admin):
            return redirect('/accounts/login/')
        return view_func(request, *args, **kwargs)
    return wrapper
