from datetime import date

from django.shortcuts import render, get_object_or_404

from .models import Event


# ---------------------------------------------------------------------------
# Per-type display metadata used in every event view
# ---------------------------------------------------------------------------
EVENT_COLORS = {
    'parade':      '#1A3A6B',   # Blue
    'competition': '#C0392B',   # Red
    'training':    '#1a6b3a',   # Green
    'church':      '#8e44ad',   # Purple
    'other':       '#b8860b',   # Gold / amber
}

EVENT_ICONS = {
    'parade':      'fas fa-flag',
    'competition': 'fas fa-trophy',
    'training':    'fas fa-chalkboard-teacher',
    'church':      'fas fa-church',
    'other':       'fas fa-calendar-day',
}


def _base_qs():
    """Reusable published-event queryset with company pre-fetched."""
    return (
        Event.objects
        .filter(is_published=True)
        .select_related('company')
    )


def events_list(request):
    """
    Public listing of all published events split into two groups:

      upcoming  — date >= today, ordered soonest first
      past      — date <  today, ordered most-recent first

    The template uses a client-side tab switcher to toggle between the two.
    """
    today = date.today()

    upcoming = (
        _base_qs()
        .filter(date__gte=today)
        .order_by('date', 'start_time')
    )
    past = (
        _base_qs()
        .filter(date__lt=today)
        .order_by('-date', 'start_time')
    )

    context = {
        'page_title':    'Events',
        'upcoming':      upcoming,
        'past':          past,
        'today':         today,
        'event_icons':   EVENT_ICONS,
        'event_colors':  EVENT_COLORS,
    }
    return render(request, 'events/events_list.html', context)


def event_detail(request, pk):
    """
    Full detail page for a single published event.

    Related events are chosen by:
      1. Same event_type (excluding this event)
      2. Ordered by proximity to this event's date
      3. Capped at 4
    """
    event = get_object_or_404(Event, pk=pk, is_published=True)
    today = date.today()

    # Related events — same type, upcoming first, then recent past
    related = (
        _base_qs()
        .filter(event_type=event.event_type)
        .exclude(pk=event.pk)
        .order_by('date', 'start_time')[:4]
    )

    context = {
        'page_title':  event.title,
        'event':       event,
        'today':       today,
        'related':     related,
        'icon':        EVENT_ICONS.get(event.event_type, 'fas fa-calendar-day'),
        'color':       EVENT_COLORS.get(event.event_type, '#1A3A6B'),
        'event_icons': EVENT_ICONS,
        'event_colors': EVENT_COLORS,
    }
    return render(request, 'events/event_detail.html', context)
