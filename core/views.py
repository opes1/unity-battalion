from datetime import date

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import BattalionInfo, ContactInfo, ContactMessage, CoreValue, LeadershipProfile
from events.models import Event
from gallery.models import Album

# Colour map for event-type badges on the homepage
EVENT_COLORS = {
    'parade':      '#1A3A6B',
    'competition': '#C0392B',
    'training':    '#1a6b3a',
    'church':      '#8e44ad',
    'other':       '#b8860b',
}


def home(request):
    """
    Renders the public homepage.

    Fetches the next 3 published, upcoming events to show in the
    Upcoming Events section.  Falls back to static placeholder cards
    in the template when the queryset is empty.
    """
    today = date.today()
    upcoming_events = (
        Event.objects
        .filter(is_published=True, date__gte=today)
        .select_related('company')
        .order_by('date', 'start_time')[:3]
    )
    recent_albums = (
        Album.objects
        .select_related('company')
        .prefetch_related('items')
        .order_by('-created_at')[:6]
    )
    context = {
        'page_title':      'Home',
        'upcoming_events': upcoming_events,
        'recent_albums':   recent_albums,
        'battalion_info':  BattalionInfo.get_solo(),
        'core_values':     CoreValue.objects.order_by('order'),
        'contact_info':    ContactInfo.get_solo(),
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    Renders the public About Us page.

    Fetches:
      • battalion_info  — singleton BattalionInfo record (created with
                          empty defaults if it hasn't been filled in yet).
      • core_values     — all CoreValue objects ordered by `order`.
      • leadership      — active LeadershipProfile objects ordered by `order`.

    The template handles empty fields gracefully by showing fallback
    placeholder text for any field that hasn't been filled in yet.
    """
    battalion_info = BattalionInfo.get_solo()
    core_values    = CoreValue.objects.order_by('order', 'title')
    leadership     = LeadershipProfile.objects.filter(
        is_active=True
    ).order_by('order', 'name')

    context = {
        'page_title':     'About Us',
        'battalion_info': battalion_info,
        'core_values':    core_values,
        'leadership':     leadership,
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """
    Renders the public Contact page and handles form submissions.

    GET:
      Fetches the ContactInfo singleton (created with blank defaults if
      absent) and renders the empty contact form.

    POST:
      Validates the submitted fields.  On success, saves a ContactMessage
      record, flashes a success notification via Django's messages
      framework, and redirects back to this page (PRG pattern — prevents
      duplicate submissions on browser refresh).
      On error, re-renders the form with the user's input and inline
      error messages so they can correct and resubmit.
    """
    contact_info = ContactInfo.get_solo()

    if request.method == 'POST':
        # ---- Collect raw input ------------------------------------------
        name         = request.POST.get('name',    '').strip()
        email        = request.POST.get('email',   '').strip()
        phone        = request.POST.get('phone',   '').strip()
        subject      = request.POST.get('subject', '').strip()
        msg_body     = request.POST.get('message', '').strip()

        # ---- Validate ---------------------------------------------------
        errors = {}
        if not name:
            errors['name'] = 'Your name is required.'
        if not email:
            errors['email'] = 'Your email address is required.'
        elif '@' not in email:
            errors['email'] = 'Please enter a valid email address.'
        if not subject:
            errors['subject'] = 'A subject line is required.'
        if not msg_body:
            errors['message'] = 'Please write a message before sending.'

        if not errors:
            # ---- Save & redirect (PRG pattern) --------------------------
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=msg_body,
            )
            messages.success(
                request,
                'Thank you for your message! We will get back to you as soon as possible.',
            )
            return redirect(reverse('core:contact'))

        # ---- Re-render form with errors & preserved input ---------------
        context = {
            'page_title':   'Contact Us',
            'contact_info': contact_info,
            'errors':       errors,
            'form_data': {
                'name':    name,
                'email':   email,
                'phone':   phone,
                'subject': subject,
                'message': msg_body,
            },
        }
        return render(request, 'core/contact.html', context)

    # ---- GET ------------------------------------------------------------
    context = {
        'page_title':   'Contact Us',
        'contact_info': contact_info,
    }
    return render(request, 'core/contact.html', context)
