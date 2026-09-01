from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST


# ──────────────────────────────────────────────────────────────────
# Super Admin Login  —  /battalion-control/
# ──────────────────────────────────────────────────────────────────

def super_login(request):
    """
    Separate, hidden login portal for super admins only.

    The URL /battalion-control/ is deliberately non-obvious so it
    does not appear in public navigation. It renders a completely
    standalone page (no navbar / footer) for extra discretion.

    GET  → render the standalone form.
    POST → authenticate, verify role = super_admin, then redirect.

    A non-super-admin who somehow finds this URL and tries to
    log in will be rejected — only super_admin role is permitted here.
    """
    # Already logged in as super_admin — send to super dashboard
    if request.user.is_authenticated:
        if request.user.is_super_admin:
            return redirect('/super-dashboard/')
        # Not a super admin — send them home
        return redirect('core:home')

    error    = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None or not user.is_active:
            # Use a generic message — don't confirm whether the user exists
            error = 'Access denied. Invalid credentials.'

        elif not user.is_super_admin:
            # Valid user but wrong role — block silently with the same message
            error = 'Access denied. Invalid credentials.'

        else:
            login(request, user)
            return redirect('/super-dashboard/')

    context = {
        'error':    error,
        'username': username,
    }
    return render(request, 'accounts/super_login.html', context)


# ──────────────────────────────────────────────────────────────────
# Logout  —  /accounts/logout/
# ──────────────────────────────────────────────────────────────────

@require_POST
def logout_view(request):
    """
    Log the current user out and redirect to the homepage.

    @require_POST ensures logout only happens via a form submission
    (not a plain link), which protects against CSRF-based logout attacks.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')
