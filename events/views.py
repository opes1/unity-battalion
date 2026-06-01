import json
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.urls import reverse

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


def events_calendar(request):
    """
    Interactive FullCalendar.js calendar page.

    Builds a JSON list of all published events so FullCalendar can render
    them as colour-coded tiles on the monthly/weekly/list view.
    The JSON is embedded directly in the template — no separate API needed.
    """
    today = date.today()
    all_events = _base_qs().order_by('date', 'start_time')

    # Also pass upcoming events for the list panel below the calendar
    upcoming = (
        _base_qs()
        .filter(date__gte=today)
        .order_by('date', 'start_time')[:8]
    )

    # ---- Build FullCalendar event objects ----
    fc_events = []
    for ev in all_events:
        # FullCalendar wants ISO datetime strings
        start = ev.date.isoformat()
        if ev.start_time:
            start = f"{ev.date.isoformat()}T{ev.start_time.strftime('%H:%M:%S')}"

        end = None
        if ev.end_time:
            end = f"{ev.date.isoformat()}T{ev.end_time.strftime('%H:%M:%S')}"

        fc_events.append({
            'id':    ev.pk,
            'title': ev.title,
            'start': start,
            'end':   end,
            'url':   reverse('events:event_detail', kwargs={'pk': ev.pk}),
            'backgroundColor': EVENT_COLORS.get(ev.event_type, '#1A3A6B'),
            'borderColor':     EVENT_COLORS.get(ev.event_type, '#1A3A6B'),
            'extendedProps': {
                'type_label':  ev.get_event_type_display(),
                'type_key':    ev.event_type,
                'location':    ev.location,
                'company':     ev.company.name if ev.company else 'Battalion-wide',
                'description': ev.description[:140] if ev.description else '',
                'icon':        EVENT_ICONS.get(ev.event_type, 'fas fa-calendar-day'),
            },
        })

    context = {
        'page_title':   'Event Calendar',
        'fc_events_json': json.dumps(fc_events),
        'upcoming':     upcoming,
        'today':        today,
        'event_icons':  EVENT_ICONS,
        'event_colors': EVENT_COLORS,
    }
    return render(request, 'events/events_calendar.html', context)


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
