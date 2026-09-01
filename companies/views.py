from datetime import date

from django.shortcuts import render, get_object_or_404

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

    if meeting_day and meeting_day in dict(Company.MeetingDay.choices):
        companies = companies.filter(meeting_day=meeting_day)

    context = {
        'page_title':         'Our Companies',
        'companies':          companies,
        'meeting_days':       Company.MeetingDay.choices,
        'filter_meeting_day': meeting_day,
        'total_count':        companies.count(),
    }
    return render(request, 'companies/companies_list.html', context)


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
