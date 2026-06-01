import json
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Company


# ---------------------------------------------------------------------------
# Section metadata — colours and icons matching the programs app
# ---------------------------------------------------------------------------
SECTION_META = {
    'anchor_boys': {'icon': 'fas fa-anchor',    'color': 'red',   'label': 'Anchor Boys',     'age': 'Ages 5–8'},
    'juniors':     {'icon': 'fas fa-star',       'color': 'blue',  'label': 'Juniors',         'age': 'Ages 8–11'},
    'company':     {'icon': 'fas fa-shield-alt', 'color': 'gold',  'label': 'Company Section', 'age': 'Ages 11–15'},
    'seniors':     {'icon': 'fas fa-crown',      'color': 'green', 'label': 'Seniors',         'age': 'Ages 15–18+'},
}


def companies_list(request):
    """
    Public listing of all active Boys Brigade companies.

    Supports GET-based filtering:
        ?meeting_day=SAT      — filter by day abbreviation (MON … SUN)
        ?section=anchor_boys  — filter companies that offer a given section

    The queryset prefetches 'admins' (User objects linked via FK) so
    the template can show officer count without extra queries.
    """
    companies = (
        Company.objects
        .filter(is_active=True)
        .prefetch_related('admins')
        .order_by('name')
    )

    # ---- Optional GET filters ----
    meeting_day = request.GET.get('meeting_day', '').strip().upper()
    section     = request.GET.get('section',     '').strip().lower()

    if meeting_day and meeting_day in dict(Company.MeetingDay.choices):
        companies = companies.filter(meeting_day=meeting_day)

    if section and section in SECTION_META:
        # PostgreSQL JSONField @> containment: checks if array contains [section]
        companies = companies.filter(sections_offered__contains=[section])

    context = {
        'page_title':         'Our Companies',
        'companies':          companies,
        'meeting_days':       Company.MeetingDay.choices,
        'sections':           Company.Section.choices,
        'section_meta':       SECTION_META,
        'filter_meeting_day': meeting_day,
        'filter_section':     section,
        'total_count':        companies.count(),
    }
    return render(request, 'companies/companies_list.html', context)


def companies_map(request):
    """
    Interactive Leaflet.js map of all active companies.

    Builds a JSON list of companies that have latitude + longitude set.
    The JSON is embedded directly in the template for Leaflet to consume —
    no separate API endpoint required.

    Companies without coordinates still appear in the list below the map.
    """
    companies = Company.objects.filter(is_active=True).order_by('name')

    # ---- Build JSON payload for Leaflet map pins ----
    map_pins = []
    for company in companies:
        if company.latitude is not None and company.longitude is not None:
            # Format time as "4:00 PM" — strftime %-I removes leading zero
            try:
                time_str = company.meeting_time.strftime('%I:%M %p').lstrip('0') if company.meeting_time else ''
            except Exception:
                time_str = str(company.meeting_time) if company.meeting_time else ''

            map_pins.append({
                'pk':          company.pk,
                'name':        company.name,
                'church':      company.church,
                'location':    company.location,
                'meeting_day': company.get_meeting_day_display(),
                'meeting_time': time_str,
                'sections':    company.sections_display,
                'lat':         company.latitude,
                'lng':         company.longitude,
                'url':         reverse('companies:company_detail', kwargs={'pk': company.pk}),
            })

    context = {
        'page_title':      'Company Map',
        'companies':       companies,
        'map_pins_json':   json.dumps(map_pins),
        'has_coordinates': bool(map_pins),
        'pin_count':       len(map_pins),
        'section_meta':    SECTION_META,
    }
    return render(request, 'companies/companies_map.html', context)


def company_detail(request, pk):
    """
    Public profile page for a single company.

    Fetches:
      officers          — approved company_admin users linked to this company
      upcoming_events   — published future events scoped to this company
      albums            — gallery albums belonging to this company
      sections_enriched — section list with icon/colour metadata attached
    """
    company = get_object_or_404(Company, pk=pk, is_active=True)

    # ---- Officers: approved admins for this company ----
    officers = (
        company.admins
        .filter(is_active=True, is_approved=True)
        .order_by('first_name', 'last_name')
    )

    # ---- Upcoming published events for this company ----
    today = date.today()
    upcoming_events = (
        company.events
        .filter(is_published=True, date__gte=today)
        .order_by('date', 'start_time')[:6]
    )

    # ---- Gallery albums (newest first, limited to 6) ----
    albums = (
        company.albums
        .prefetch_related('items')
        .order_by('-created_at')[:6]
    )

    # ---- Enrich sections_offered with icon/colour meta ----
    sections_enriched = [
        {
            'key':   s,
            'label': SECTION_META[s]['label'],
            'icon':  SECTION_META[s]['icon'],
            'color': SECTION_META[s]['color'],
            'age':   SECTION_META[s]['age'],
        }
        for s in company.sections_offered
        if s in SECTION_META
    ]

    context = {
        'page_title':        company.name,
        'company':           company,
        'officers':          officers,
        'upcoming_events':   upcoming_events,
        'albums':            albums,
        'sections_enriched': sections_enriched,
        'today':             today,
    }
    return render(request, 'companies/company_detail.html', context)
