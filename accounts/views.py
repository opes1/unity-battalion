from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST


# ──────────────────────────────────────────────────────────────────
# Internal helper
# ──────────────────────────────────────────────────────────────────

def _redirect_for_role(user):
    """
    Return the correct redirect response for an authenticated user
    based on their role.
      super_admin   → /super-dashboard/
      company_admin → /company-dashboard/
    """
    if user.is_super_admin:
        return redirect('/super-dashboard/')
    return redirect('/company-dashboard/')


# ──────────────────────────────────────────────────────────────────
# Company Admin Login  —  /accounts/login/
# ──────────────────────────────────────────────────────────────────

def company_login(request):
    """
    Login page for company admins ONLY  —  /accounts/login/

    GET  → render the login form.
    POST → authenticate, verify role = company_admin, check approval,
           then redirect to /company-dashboard/.

    Super admins are explicitly blocked here; they must use the
    hidden /battalion-control/ portal.

    A ?next= query param is honoured so Django's @login_required
    decorator can send users back where they came from after logging in.
    """
    # Already logged in — send straight to their dashboard
    if request.user.is_authenticated:
        return _redirect_for_role(request.user)

    error    = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            # Wrong credentials — don't reveal which field is wrong
            error = 'Invalid username or password. Please try again.'

        elif not user.is_active:
            error = 'This account has been deactivated. Contact the administrator.'

        elif not user.is_company_admin:
            # Super admin (or unknown role) trying the wrong portal —
            # use a generic message so the role distinction isn't exposed
            error = 'This login is for company staff only. Please use the correct portal.'

        elif not user.is_approved:
            # Valid company admin but not yet approved by the super admin
            error = (
                'Your account is pending approval. '
                'Please contact the Battalion Administrator.'
            )

        else:
            # All checks passed — log in and redirect to company dashboard
            login(request, user)

            # Honour ?next= if present and safe (stays on this domain)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)

            return redirect('/company-dashboard/')

    context = {
        'error':    error,
        'username': username,
        'next':     request.GET.get('next', ''),
    }
    return render(request, 'accounts/login.html', context)


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

    A regular company_admin who somehow finds this URL and tries to
    log in will be rejected — only super_admin role is permitted here.
    """
    # Already logged in as super_admin — send to super dashboard
    if request.user.is_authenticated:
        if request.user.is_super_admin:
            return redirect('/super-dashboard/')
        # Company admin accidentally hit this URL — send them home
        return redirect('/company-dashboard/')

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
