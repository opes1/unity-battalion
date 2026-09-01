"""
Dashboard views for Unity Battalion Council.

All views in this module are protected by @super_admin_required, which
redirects unauthenticated or non-super-admin visitors to the hidden
login portal at /battalion-control/.
"""

from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from companies.models import Company
from core.models import (
    BattalionInfo, ContactInfo, ContactMessage,
    CoreValue, LeadershipProfile,
)
from events.models import Event
from gallery.models import Album, GalleryItem
from resources.models import Resource

from .decorators import super_admin_required


# ======================================================================
# Internal helpers
# ======================================================================

def _sidebar_counts():
    """
    Returns a dict of counts used to render notification badges in
    the sidebar.  Called by every view so badges stay up-to-date on
    every page load.
    """
    return {
        'sidebar_unread_messages': (
            ContactMessage.objects.filter(is_read=False).count()
        ),
    }


# ======================================================================
# Super-Admin Overview
# ======================================================================

@super_admin_required
def super_dashboard(request):
    """
    Main super-admin overview page.

    Shows:
      • Four stats cards (companies, events, messages, albums)
      • Latest 5 unread contact messages
      • Quick-action buttons
    """
    today = date.today()

    stats = {
        'total_companies':    Company.objects.count(),
        'active_companies':   Company.objects.filter(is_active=True).count(),
        'unread_messages':    ContactMessage.objects.filter(is_read=False).count(),
        'total_messages':     ContactMessage.objects.count(),
        'upcoming_events':    Event.objects.filter(
                                  is_published=True, date__gte=today
                              ).count(),
        'total_events':       Event.objects.count(),
        'total_albums':       Album.objects.count(),
    }

    recent_messages = (
        ContactMessage.objects
        .order_by('-created_at')[:5]
    )

    context = {
        'page_title': 'Dashboard Overview',
        'stats':           stats,
        'recent_messages': recent_messages,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/super_dashboard.html', context)


# ======================================================================
# Company Management
# ======================================================================

@super_admin_required
def manage_companies(request):
    """
    Lists all companies with quick activate/deactivate toggles.
    """
    companies = (
        Company.objects
        .prefetch_related('admins')
        .order_by('name')
    )
    context = {
        'page_title': 'Manage Companies',
        'companies': companies,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_companies.html', context)


@super_admin_required
def edit_company(request, pk):
    """
    GET  — Renders a full edit form for the given company.
    POST — Validates and saves changes directly (super-admin bypass).
    """
    company = get_object_or_404(Company, pk=pk)
    sections_all = Company.Section.choices   # list of (value, label) tuples
    meeting_days = Company.MeetingDay.choices

    errors = {}

    if request.method == 'POST':
        # ---- Collect fields -----------------------------------------
        name      = request.POST.get('name', '').strip()
        church    = request.POST.get('church', '').strip()
        location  = request.POST.get('location', '').strip()
        m_day     = request.POST.get('meeting_day', '').strip()
        m_time    = request.POST.get('meeting_time', '').strip()
        sections  = request.POST.getlist('sections_offered')
        about     = request.POST.get('about', '').strip()
        phone     = request.POST.get('phone', '').strip()
        email     = request.POST.get('email', '').strip()
        website   = request.POST.get('website', '').strip()
        captain_name  = request.POST.get('captain_name', '').strip()
        captain_phone = request.POST.get('captain_phone', '').strip()
        captain_email = request.POST.get('captain_email', '').strip()
        est_date  = request.POST.get('date_established', '').strip() or None
        lat_raw   = request.POST.get('latitude', '').strip() or None
        lng_raw   = request.POST.get('longitude', '').strip() or None
        is_active = 'is_active' in request.POST

        # ---- Validate -----------------------------------------------
        if not name:
            errors['name'] = 'Company name is required.'
        if not church:
            errors['church'] = 'Church name is required.'
        if not location:
            errors['location'] = 'Location is required.'
        if not m_day:
            errors['meeting_day'] = 'Meeting day is required.'
        if not m_time:
            errors['meeting_time'] = 'Meeting time is required.'

        valid_sections = [c[0] for c in sections_all]
        sections = [s for s in sections if s in valid_sections]

        latitude  = None
        longitude = None
        if lat_raw:
            try:
                latitude = float(lat_raw)
            except ValueError:
                errors['latitude'] = 'Latitude must be a number, e.g. 6.4550'
        if lng_raw:
            try:
                longitude = float(lng_raw)
            except ValueError:
                errors['longitude'] = 'Longitude must be a number, e.g. 3.3841'

        if not errors:
            company.name             = name
            company.church           = church
            company.location         = location
            company.meeting_day      = m_day
            company.meeting_time     = m_time
            company.sections_offered = sections
            company.about            = about
            company.phone            = phone
            company.email            = email
            company.website          = website
            company.captain_name     = captain_name
            company.captain_phone    = captain_phone
            company.captain_email    = captain_email
            company.date_established = est_date or None
            company.latitude         = latitude
            company.longitude        = longitude
            company.is_active        = is_active
            company.save()

            # File uploads — save separately so other fields aren't re-saved
            if request.FILES.get('logo'):
                company.logo = request.FILES['logo']
                company.save(update_fields=['logo'])
            if request.FILES.get('banner'):
                company.banner = request.FILES['banner']
                company.save(update_fields=['banner'])

            messages.success(
                request,
                f'"{company.name}" has been updated successfully.',
            )
            return redirect('dashboard:manage_companies')

        # Re-render with errors — build a form-data dict for repopulation
        form_data = {
            'name': name, 'church': church, 'location': location,
            'meeting_day': m_day, 'meeting_time': m_time,
            'sections_offered': sections, 'about': about,
            'phone': phone, 'email': email, 'website': website,
            'captain_name': captain_name, 'captain_phone': captain_phone,
            'captain_email': captain_email,
            'date_established': est_date or '',
            'latitude': lat_raw or '', 'longitude': lng_raw or '',
            'is_active': is_active,
        }
    else:
        # Pre-populate from existing company record
        form_data = {
            'name':             company.name,
            'church':           company.church,
            'location':         company.location,
            'meeting_day':      company.meeting_day,
            'meeting_time':     company.meeting_time.strftime('%H:%M') if company.meeting_time else '',
            'sections_offered': company.sections_offered or [],
            'about':            company.about,
            'phone':            company.phone,
            'email':            company.email,
            'website':          company.website,
            'captain_name':     company.captain_name,
            'captain_phone':    company.captain_phone,
            'captain_email':    company.captain_email,
            'date_established': company.date_established.isoformat() if company.date_established else '',
            'latitude':         company.latitude if company.latitude is not None else '',
            'longitude':        company.longitude if company.longitude is not None else '',
            'is_active':        company.is_active,
        }

    context = {
        'page_title':   f'Edit — {company.name}',
        'company':      company,
        'form_data':    form_data,
        'errors':       errors,
        'sections_all': sections_all,
        'meeting_days': meeting_days,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_company.html', context)


@super_admin_required
def add_company(request):
    """
    GET  — Renders a blank form to register a new company.
    POST — Validates and creates the Company directly (super-admin bypass).
    """
    sections_all = Company.Section.choices
    meeting_days = Company.MeetingDay.choices

    errors = {}

    if request.method == 'POST':
        # ---- Collect fields -----------------------------------------
        name      = request.POST.get('name', '').strip()
        church    = request.POST.get('church', '').strip()
        location  = request.POST.get('location', '').strip()
        m_day     = request.POST.get('meeting_day', '').strip()
        m_time    = request.POST.get('meeting_time', '').strip()
        sections  = request.POST.getlist('sections_offered')
        about     = request.POST.get('about', '').strip()
        phone     = request.POST.get('phone', '').strip()
        email     = request.POST.get('email', '').strip()
        website   = request.POST.get('website', '').strip()
        captain_name  = request.POST.get('captain_name', '').strip()
        captain_phone = request.POST.get('captain_phone', '').strip()
        captain_email = request.POST.get('captain_email', '').strip()
        est_date  = request.POST.get('date_established', '').strip() or None
        lat_raw   = request.POST.get('latitude', '').strip() or None
        lng_raw   = request.POST.get('longitude', '').strip() or None
        is_active = 'is_active' in request.POST

        # ---- Validate -----------------------------------------------
        if not name:
            errors['name'] = 'Company name is required.'
        if not church:
            errors['church'] = 'Church name is required.'
        if not location:
            errors['location'] = 'Location is required.'
        if not m_day:
            errors['meeting_day'] = 'Meeting day is required.'
        if not m_time:
            errors['meeting_time'] = 'Meeting time is required.'

        valid_sections = [c[0] for c in sections_all]
        sections = [s for s in sections if s in valid_sections]

        latitude  = None
        longitude = None
        if lat_raw:
            try:
                latitude = float(lat_raw)
            except ValueError:
                errors['latitude'] = 'Latitude must be a number, e.g. 6.4550'
        if lng_raw:
            try:
                longitude = float(lng_raw)
            except ValueError:
                errors['longitude'] = 'Longitude must be a number, e.g. 3.3841'

        if not errors:
            company = Company.objects.create(
                name=name,
                church=church,
                location=location,
                meeting_day=m_day,
                meeting_time=m_time,
                sections_offered=sections,
                about=about,
                phone=phone,
                email=email,
                website=website,
                captain_name=captain_name,
                captain_phone=captain_phone,
                captain_email=captain_email,
                date_established=est_date or None,
                latitude=latitude,
                longitude=longitude,
                is_active=is_active,
            )

            if request.FILES.get('logo'):
                company.logo = request.FILES['logo']
                company.save(update_fields=['logo'])
            if request.FILES.get('banner'):
                company.banner = request.FILES['banner']
                company.save(update_fields=['banner'])

            messages.success(
                request,
                f'"{company.name}" has been added successfully.',
            )
            return redirect('dashboard:manage_companies')

        # Re-render with errors — build a form-data dict for repopulation
        form_data = {
            'name': name, 'church': church, 'location': location,
            'meeting_day': m_day, 'meeting_time': m_time,
            'sections_offered': sections, 'about': about,
            'phone': phone, 'email': email, 'website': website,
            'captain_name': captain_name, 'captain_phone': captain_phone,
            'captain_email': captain_email,
            'date_established': est_date or '',
            'latitude': lat_raw or '', 'longitude': lng_raw or '',
            'is_active': is_active,
        }
    else:
        form_data = {
            'name': '', 'church': '', 'location': '',
            'meeting_day': '', 'meeting_time': '',
            'sections_offered': [], 'about': '',
            'phone': '', 'email': '', 'website': '',
            'captain_name': '', 'captain_phone': '', 'captain_email': '',
            'date_established': '', 'latitude': '', 'longitude': '',
            'is_active': True,
        }

    context = {
        'page_title':   'Add Company',
        'form_data':    form_data,
        'errors':       errors,
        'sections_all': sections_all,
        'meeting_days': meeting_days,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_company.html', context)


@super_admin_required
def toggle_company(request, pk):
    """
    POST-only.  Flips a company's is_active flag.
    Redirects back to the companies list.
    """
    if request.method == 'POST':
        company = get_object_or_404(Company, pk=pk)
        company.is_active = not company.is_active
        company.save(update_fields=['is_active'])
        verb = 'activated' if company.is_active else 'deactivated'
        messages.success(request, f'"{company.name}" has been {verb}.')
    return redirect('dashboard:manage_companies')


# ======================================================================
# User Management
# ======================================================================

@super_admin_required
def manage_users(request):
    """
    Lists all users split into Pending (not yet approved) and
    Active/Approved groups.
    """
    base_qs = (
        User.objects
        .select_related('company')
        .order_by('-date_joined')
    )
    pending_users  = base_qs.filter(is_approved=False,
                                    role=User.Role.COMPANY_ADMIN)
    approved_users = base_qs.filter(is_approved=True)

    context = {
        'page_title':     'Manage Users',
        'pending_users':  pending_users,
        'approved_users': approved_users,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_users.html', context)


@super_admin_required
def approve_user(request, pk):
    """
    POST-only.  Sets is_approved=True on a company-admin user account.
    """
    if request.method == 'POST':
        user = get_object_or_404(
            User, pk=pk, role=User.Role.COMPANY_ADMIN
        )
        user.is_approved = True
        user.is_active   = True
        user.save(update_fields=['is_approved', 'is_active'])
        display = user.get_full_name() or user.username
        messages.success(request, f'{display} has been approved.')
    return redirect('dashboard:manage_users')


# ======================================================================
# Event Management
# ======================================================================

@super_admin_required
def manage_events(request):
    """
    Lists all events with quick publish/unpublish toggle handled inline
    via a POST form on this same URL.
    """
    if request.method == 'POST':
        # Inline toggle — event_id + action posted from the table row
        event_id = request.POST.get('event_id')
        action   = request.POST.get('action')
        if event_id and action in ('publish', 'unpublish'):
            try:
                ev = Event.objects.get(pk=event_id)
                ev.is_published = (action == 'publish')
                ev.save(update_fields=['is_published'])
                verb = 'published' if ev.is_published else 'unpublished'
                messages.success(request, f'"{ev.title}" has been {verb}.')
            except Event.DoesNotExist:
                pass
        return redirect('dashboard:manage_events')

    events = (
        Event.objects
        .select_related('company')
        .order_by('-date', 'start_time')
    )
    context = {
        'page_title': 'Manage Events',
        'events':     events,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_events.html', context)


# ======================================================================
# Contact Messages
# ======================================================================

@super_admin_required
def view_messages(request):
    """
    Lists all contact messages submitted through the public form.
    Supports marking individual messages as read/unread via inline POST.
    """
    if request.method == 'POST':
        msg_id = request.POST.get('message_id')
        action = request.POST.get('action')
        if msg_id and action in ('read', 'unread'):
            try:
                cm = ContactMessage.objects.get(pk=msg_id)
                cm.is_read = (action == 'read')
                cm.save(update_fields=['is_read'])
            except ContactMessage.DoesNotExist:
                pass
        return redirect('dashboard:view_messages')

    all_messages = ContactMessage.objects.order_by('-created_at')
    unread_count = all_messages.filter(is_read=False).count()

    context = {
        'page_title':    'Contact Messages',
        'messages_list': all_messages,
        'unread_count':  unread_count,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/view_messages.html', context)


# ======================================================================
# Events CRUD  (super-admin only)
# ======================================================================

@super_admin_required
def add_event(request):
    """GET — blank event form.  POST — create Event, redirect to manage_events."""
    companies   = Company.objects.filter(is_active=True).order_by('name')
    event_types = Event.EventType.choices
    errors      = {}

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        event_type   = request.POST.get('event_type', '').strip()
        date_str     = request.POST.get('date', '').strip()
        start_time   = request.POST.get('start_time', '').strip() or None
        end_time     = request.POST.get('end_time', '').strip() or None
        location     = request.POST.get('location', '').strip()
        description  = request.POST.get('description', '').strip()
        company_id   = request.POST.get('company', '').strip() or None
        is_published = 'is_published' in request.POST

        if not title:
            errors['title'] = 'Event title is required.'
        if not event_type:
            errors['event_type'] = 'Event type is required.'
        if not date_str:
            errors['date'] = 'Event date is required.'

        company = None
        if not errors and company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                errors['company'] = 'Selected company does not exist.'

        if not errors:
            ev = Event.objects.create(
                title=title,
                event_type=event_type,
                date=date_str,
                start_time=start_time,
                end_time=end_time,
                location=location,
                description=description,
                company=company,
                is_published=is_published,
                created_by=request.user,
            )
            if request.FILES.get('banner'):
                ev.banner = request.FILES['banner']
                ev.save(update_fields=['banner'])
            messages.success(request, f'Event "{ev.title}" created successfully.')
            return redirect('dashboard:manage_events')

        form_data = {
            'title': title, 'event_type': event_type, 'date': date_str,
            'start_time': start_time or '', 'end_time': end_time or '',
            'location': location, 'description': description,
            'company': company_id or '', 'is_published': is_published,
        }
    else:
        form_data = {
            'title': '', 'event_type': '', 'date': '',
            'start_time': '', 'end_time': '', 'location': '',
            'description': '', 'company': '', 'is_published': False,
        }

    context = {
        'page_title':  'Add Event',
        'companies':   companies,
        'event_types': event_types,
        'form_data':   form_data,
        'errors':      errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_event.html', context)


@super_admin_required
def edit_event(request, pk):
    """GET — pre-filled event form.  POST — save changes, redirect."""
    event       = get_object_or_404(Event, pk=pk)
    companies   = Company.objects.filter(is_active=True).order_by('name')
    event_types = Event.EventType.choices
    errors      = {}

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        event_type   = request.POST.get('event_type', '').strip()
        date_str     = request.POST.get('date', '').strip()
        start_time   = request.POST.get('start_time', '').strip() or None
        end_time     = request.POST.get('end_time', '').strip() or None
        location     = request.POST.get('location', '').strip()
        description  = request.POST.get('description', '').strip()
        company_id   = request.POST.get('company', '').strip() or None
        is_published = 'is_published' in request.POST

        if not title:
            errors['title'] = 'Event title is required.'
        if not event_type:
            errors['event_type'] = 'Event type is required.'
        if not date_str:
            errors['date'] = 'Event date is required.'

        company = None
        if not errors and company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                errors['company'] = 'Selected company does not exist.'

        if not errors:
            event.title        = title
            event.event_type   = event_type
            event.date         = date_str
            event.start_time   = start_time
            event.end_time     = end_time
            event.location     = location
            event.description  = description
            event.company      = company
            event.is_published = is_published
            if request.FILES.get('banner'):
                event.banner = request.FILES['banner']
            event.save()
            messages.success(request, f'Event "{event.title}" updated successfully.')
            return redirect('dashboard:manage_events')

        form_data = {
            'title': title, 'event_type': event_type, 'date': date_str,
            'start_time': start_time or '', 'end_time': end_time or '',
            'location': location, 'description': description,
            'company': company_id or '', 'is_published': is_published,
        }
    else:
        form_data = {
            'title':        event.title,
            'event_type':   event.event_type,
            'date':         event.date.isoformat(),
            'start_time':   event.start_time.strftime('%H:%M') if event.start_time else '',
            'end_time':     event.end_time.strftime('%H:%M') if event.end_time else '',
            'location':     event.location,
            'description':  event.description,
            'company':      event.company_id or '',
            'is_published': event.is_published,
        }

    context = {
        'page_title':  f'Edit — {event.title}',
        'event':       event,
        'companies':   companies,
        'event_types': event_types,
        'form_data':   form_data,
        'errors':      errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_event.html', context)


@super_admin_required
def delete_event(request, pk):
    """POST-only.  Deletes the event and redirects to manage_events."""
    if request.method == 'POST':
        ev = get_object_or_404(Event, pk=pk)
        title = ev.title
        ev.delete()
        messages.success(request, f'Event "{title}" has been deleted.')
    return redirect('dashboard:manage_events')


# ======================================================================
# Gallery Management  (super-admin only)
# ======================================================================

@super_admin_required
def manage_gallery(request):
    """Lists all albums with company, item count, and created date."""
    albums = (
        Album.objects
        .select_related('company')
        .order_by('-created_at')
    )
    context = {
        'page_title': 'Gallery Management',
        'albums':     albums,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_gallery.html', context)


@super_admin_required
def add_album(request):
    """
    GET  — blank album form with optional multi-photo upload.
    POST — create Album, attach GalleryItems for every uploaded photo,
           auto-set cover from the first photo if none supplied.
    """
    companies = Company.objects.filter(is_active=True).order_by('name')
    errors    = {}

    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        company_id  = request.POST.get('company', '').strip() or None

        if not title:
            errors['title'] = 'Album title is required.'

        company = None
        if not errors and company_id:
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                errors['company'] = 'Selected company does not exist.'

        if not errors:
            album = Album.objects.create(
                title=title,
                description=description,
                company=company,
            )

            # ---- Cover photo ----------------------------------------
            if request.FILES.get('cover_photo'):
                album.cover_photo = request.FILES['cover_photo']
                album.save(update_fields=['cover_photo'])

            # ---- Bulk photo upload ----------------------------------
            photos = request.FILES.getlist('photos')
            for i, photo in enumerate(photos):
                GalleryItem.objects.create(
                    album=album,
                    file=photo,
                    media_type=GalleryItem.MediaType.PHOTO,
                    order=i,
                )

            # Auto-set cover from first uploaded photo if no cover supplied
            if photos and not album.cover_photo:
                first_item = album.items.order_by('order').first()
                if first_item and first_item.file:
                    album.cover_photo = first_item.file
                    album.save(update_fields=['cover_photo'])

            photo_count = len(photos)
            photo_msg   = f' {photo_count} photo{"s" if photo_count != 1 else ""} uploaded.' if photo_count else ''
            messages.success(
                request,
                f'Album "{album.title}" created.{photo_msg}',
            )
            return redirect('dashboard:manage_gallery')

        form_data = {
            'title': title, 'description': description, 'company': company_id or '',
        }
    else:
        form_data = {'title': '', 'description': '', 'company': ''}

    context = {
        'page_title': 'Add Album',
        'companies':  companies,
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_album.html', context)


@super_admin_required
def add_photos_to_album(request, pk):
    """
    GET  — shows a multi-photo upload form for an existing album.
    POST — creates a GalleryItem for every uploaded file, appending
           after any existing items (preserves existing order).
    Redirects back to manage_gallery after upload.
    """
    album = get_object_or_404(Album, pk=pk)

    if request.method == 'POST':
        photos = request.FILES.getlist('photos')

        if not photos:
            messages.warning(request, 'No photos were selected.')
            return redirect('dashboard:add_photos_to_album', pk=pk)

        # Start ordering after the current last item
        existing_count = album.items.count()
        for i, photo in enumerate(photos):
            GalleryItem.objects.create(
                album=album,
                file=photo,
                media_type=GalleryItem.MediaType.PHOTO,
                order=existing_count + i,
            )

        # Auto-set cover if the album has none yet
        if not album.cover_photo:
            first_item = album.items.order_by('order').first()
            if first_item and first_item.file:
                album.cover_photo = first_item.file
                album.save(update_fields=['cover_photo'])

        count = len(photos)
        messages.success(
            request,
            f'{count} photo{"s" if count != 1 else ""} added to "{album.title}".',
        )
        return redirect('dashboard:manage_gallery')

    context = {
        'page_title': f'Add Photos — {album.title}',
        'album':      album,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_photos_to_album.html', context)


@super_admin_required
def delete_album(request, pk):
    """POST-only.  Deletes the album (and cascade its items) and redirects."""
    if request.method == 'POST':
        album = get_object_or_404(Album, pk=pk)
        title = album.title
        album.delete()
        messages.success(request, f'Album "{title}" and all its photos have been deleted.')
    return redirect('dashboard:manage_gallery')


# ======================================================================
# Resources Management  (super-admin only)
# ======================================================================

@super_admin_required
def manage_resources(request):
    """Lists all resources with category, audience, file, and published status."""
    resources = Resource.objects.order_by('-uploaded_at')
    context = {
        'page_title': 'Resources Management',
        'resources':  resources,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_resources.html', context)


@super_admin_required
def add_resource(request):
    """GET — blank resource form.  POST — create Resource, redirect."""
    category_choices = Resource.Category.choices
    audience_choices = Resource.Audience.choices
    errors           = {}

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        description  = request.POST.get('description', '').strip()
        category     = request.POST.get('category', '').strip()
        audience     = request.POST.get('audience', '').strip()
        is_published = 'is_published' in request.POST

        if not title:
            errors['title'] = 'Resource title is required.'
        if not category:
            errors['category'] = 'Category is required.'
        if not audience:
            errors['audience'] = 'Audience is required.'

        if not errors:
            resource = Resource.objects.create(
                title=title,
                description=description,
                category=category,
                audience=audience,
                is_published=is_published,
                uploaded_by=request.user,
            )
            if request.FILES.get('file'):
                resource.file = request.FILES['file']
                resource.save(update_fields=['file'])
            messages.success(request, f'Resource "{resource.title}" added successfully.')
            return redirect('dashboard:manage_resources')

        form_data = {
            'title': title, 'description': description,
            'category': category, 'audience': audience,
            'is_published': is_published,
        }
    else:
        form_data = {
            'title': '', 'description': '', 'category': '',
            'audience': '', 'is_published': False,
        }

    context = {
        'page_title':       'Add Resource',
        'category_choices': category_choices,
        'audience_choices': audience_choices,
        'form_data':        form_data,
        'errors':           errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_resource.html', context)


@super_admin_required
def delete_resource(request, pk):
    """POST-only.  Deletes the resource and redirects."""
    if request.method == 'POST':
        resource = get_object_or_404(Resource, pk=pk)
        title = resource.title
        resource.delete()
        messages.success(request, f'Resource "{title}" has been deleted.')
    return redirect('dashboard:manage_resources')


@super_admin_required
def toggle_resource(request, pk):
    """POST-only.  Flips is_published on a resource."""
    if request.method == 'POST':
        resource = get_object_or_404(Resource, pk=pk)
        resource.is_published = not resource.is_published
        resource.save(update_fields=['is_published'])
        verb = 'published' if resource.is_published else 'unpublished'
        messages.success(request, f'"{resource.title}" has been {verb}.')
    return redirect('dashboard:manage_resources')


# ======================================================================
# Content Management — About Page  (super-admin only)
# ======================================================================

@super_admin_required
def edit_about(request):
    """
    GET  — Show all BattalionInfo fields in a tabbed form.
    POST — Validate and save every field, including optional banner upload.

    Sections:
      1. Basic Identity  — name, motto, subtitle, organisation, age_range,
                           founded_year, headquarters
      2. Stats           — active_companies, boys_enrolled, bb_sections
      3. Page Content    — hero_title, history_heading, history,
                           mission, vision, bb_object
      4. CTA             — cta_heading, cta_text
      5. Banner          — banner image upload
    """
    info   = BattalionInfo.get_solo()
    errors = {}

    if request.method == 'POST':
        # ---- Section 1: Basic Identity ----------------------------------
        name         = request.POST.get('name', '').strip()
        motto        = request.POST.get('motto', '').strip()
        subtitle     = request.POST.get('subtitle', '').strip()
        organisation = request.POST.get('organisation', '').strip()
        age_range    = request.POST.get('age_range', '').strip()
        headquarters = request.POST.get('headquarters', '').strip()
        founded_raw  = request.POST.get('founded_year', '').strip()

        # ---- Section 2: Stats -------------------------------------------
        active_companies = request.POST.get('active_companies', '').strip()
        boys_enrolled    = request.POST.get('boys_enrolled', '').strip()
        bb_sections      = request.POST.get('bb_sections', '').strip()

        # ---- Section 3: Page Content ------------------------------------
        hero_title      = request.POST.get('hero_title', '').strip()
        history_heading = request.POST.get('history_heading', '').strip()
        history         = request.POST.get('history', '').strip()
        mission         = request.POST.get('mission', '').strip()
        vision          = request.POST.get('vision', '').strip()
        bb_object       = request.POST.get('bb_object', '').strip()

        # ---- Section 4: CTA ---------------------------------------------
        cta_heading = request.POST.get('cta_heading', '').strip()
        cta_text    = request.POST.get('cta_text', '').strip()

        # ---- Section 5 (new): Home Page Content -------------------------
        home_hero_title       = request.POST.get('home_hero_title', '').strip()
        home_hero_description = request.POST.get('home_hero_description', '').strip()
        years_of_service      = request.POST.get('years_of_service', '').strip()
        home_cta_heading      = request.POST.get('home_cta_heading', '').strip()
        home_cta_text         = request.POST.get('home_cta_text', '').strip()
        gallery_subtitle      = request.POST.get('gallery_subtitle', '').strip()

        # ---- Section 6 (new): Site Settings ------------------------------
        site_name             = request.POST.get('site_name', '').strip()
        site_tagline          = request.POST.get('site_tagline', '').strip()
        announcements_enabled = 'announcements_enabled' in request.POST
        announcements_text    = request.POST.get('announcements_text', '').strip()

        # ---- Section 7 (new): Home Page Sections -------------------------
        show_stats_section  = 'show_stats_section' in request.POST
        show_about_section  = 'show_about_section' in request.POST
        show_events_section = 'show_events_section' in request.POST
        show_gallery_section = 'show_gallery_section' in request.POST

        # ---- Section 8 (new): SEO & Footer -------------------------------
        seo_title              = request.POST.get('seo_title', '').strip()
        seo_description        = request.POST.get('seo_description', '').strip()
        footer_copyright_text  = request.POST.get('footer_copyright_text', '').strip()
        contact_intro_text     = request.POST.get('contact_intro_text', '').strip()

        # ---- Validate ---------------------------------------------------
        founded_year = None
        if founded_raw:
            try:
                founded_year = int(founded_raw)
                if not (1800 <= founded_year <= 2100):
                    errors['founded_year'] = 'Enter a valid four-digit year.'
            except ValueError:
                errors['founded_year'] = 'Founded year must be a number, e.g. 2005.'

        form_data = {
            'name': name, 'motto': motto, 'subtitle': subtitle,
            'organisation': organisation, 'age_range': age_range,
            'headquarters': headquarters, 'founded_year': founded_raw,
            'active_companies': active_companies, 'boys_enrolled': boys_enrolled,
            'bb_sections': bb_sections,
            'hero_title': hero_title, 'history_heading': history_heading,
            'history': history, 'mission': mission, 'vision': vision,
            'bb_object': bb_object, 'cta_heading': cta_heading, 'cta_text': cta_text,
            'home_hero_title': home_hero_title,
            'home_hero_description': home_hero_description,
            'years_of_service': years_of_service,
            'home_cta_heading': home_cta_heading,
            'home_cta_text': home_cta_text,
            'gallery_subtitle': gallery_subtitle,
            'site_name': site_name, 'site_tagline': site_tagline,
            'announcements_enabled': announcements_enabled,
            'announcements_text': announcements_text,
            'show_stats_section': show_stats_section,
            'show_about_section': show_about_section,
            'show_events_section': show_events_section,
            'show_gallery_section': show_gallery_section,
            'seo_title': seo_title, 'seo_description': seo_description,
            'footer_copyright_text': footer_copyright_text,
            'contact_intro_text': contact_intro_text,
        }

        if not errors:
            info.name             = name
            info.motto            = motto
            info.subtitle         = subtitle
            info.organisation     = organisation
            info.age_range        = age_range
            info.headquarters     = headquarters
            info.founded_year     = founded_year
            info.active_companies = active_companies
            info.boys_enrolled    = boys_enrolled
            info.bb_sections      = bb_sections
            info.hero_title       = hero_title
            info.history_heading  = history_heading
            info.history          = history
            info.mission          = mission
            info.vision           = vision
            info.bb_object        = bb_object
            info.cta_heading            = cta_heading
            info.cta_text               = cta_text
            info.home_hero_title        = home_hero_title
            info.home_hero_description  = home_hero_description
            info.years_of_service       = years_of_service
            info.home_cta_heading       = home_cta_heading
            info.home_cta_text          = home_cta_text
            info.gallery_subtitle       = gallery_subtitle
            info.site_name              = site_name
            info.site_tagline           = site_tagline
            info.announcements_enabled  = announcements_enabled
            info.announcements_text     = announcements_text
            info.show_stats_section     = show_stats_section
            info.show_about_section     = show_about_section
            info.show_events_section    = show_events_section
            info.show_gallery_section   = show_gallery_section
            info.seo_title              = seo_title
            info.seo_description        = seo_description
            info.footer_copyright_text  = footer_copyright_text
            info.contact_intro_text     = contact_intro_text
            info.save()

            # Banner upload — save separately so other fields aren't re-saved
            if request.FILES.get('banner'):
                info.banner = request.FILES['banner']
                info.save(update_fields=['banner'])

            # Hero background image upload — same pattern as banner
            if request.FILES.get('hero_bg_image'):
                info.hero_bg_image = request.FILES['hero_bg_image']
                info.save(update_fields=['hero_bg_image'])

            messages.success(request, 'About page content updated successfully.')
            return redirect('dashboard:edit_about')

    else:
        form_data = {
            'name':             info.name,
            'motto':            info.motto,
            'subtitle':         info.subtitle,
            'organisation':     info.organisation,
            'age_range':        info.age_range,
            'headquarters':     info.headquarters,
            'founded_year':     info.founded_year or '',
            'active_companies': info.active_companies,
            'boys_enrolled':    info.boys_enrolled,
            'bb_sections':      info.bb_sections,
            'hero_title':       info.hero_title,
            'history_heading':  info.history_heading,
            'history':          info.history,
            'mission':          info.mission,
            'vision':           info.vision,
            'bb_object':        info.bb_object,
            'cta_heading':           info.cta_heading,
            'cta_text':              info.cta_text,
            'home_hero_title':       info.home_hero_title,
            'home_hero_description': info.home_hero_description,
            'years_of_service':      info.years_of_service,
            'home_cta_heading':      info.home_cta_heading,
            'home_cta_text':         info.home_cta_text,
            'gallery_subtitle':      info.gallery_subtitle,
            'site_name':             info.site_name,
            'site_tagline':          info.site_tagline,
            'announcements_enabled': info.announcements_enabled,
            'announcements_text':    info.announcements_text,
            'show_stats_section':    info.show_stats_section,
            'show_about_section':    info.show_about_section,
            'show_events_section':   info.show_events_section,
            'show_gallery_section':  info.show_gallery_section,
            'seo_title':             info.seo_title,
            'seo_description':       info.seo_description,
            'footer_copyright_text': info.footer_copyright_text,
            'contact_intro_text':    info.contact_intro_text,
        }

    context = {
        'page_title': 'Edit About Page',
        'info':       info,
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_about.html', context)


# ======================================================================
# Content Management — Contact Info  (super-admin only)
# ======================================================================

@super_admin_required
def edit_contact_info(request):
    """
    GET  — Show editable fields from the ContactInfo singleton.
    POST — Validate and save changes.

    Editable fields:
      address, phone, email, office_hours,
      facebook_url, instagram_url, whatsapp_number, map_embed_url
    """
    info   = ContactInfo.get_solo()
    errors = {}

    if request.method == 'POST':
        address         = request.POST.get('address', '').strip()
        phone           = request.POST.get('phone', '').strip()
        email           = request.POST.get('email', '').strip()
        office_hours    = request.POST.get('office_hours', '').strip()
        facebook_url    = request.POST.get('facebook_url', '').strip()
        instagram_url   = request.POST.get('instagram_url', '').strip()
        whatsapp_number = request.POST.get('whatsapp_number', '').strip()
        map_embed_url   = request.POST.get('map_embed_url', '').strip()

        form_data = {
            'address': address, 'phone': phone, 'email': email,
            'office_hours': office_hours, 'facebook_url': facebook_url,
            'instagram_url': instagram_url, 'whatsapp_number': whatsapp_number,
            'map_embed_url': map_embed_url,
        }

        if not errors:
            info.address         = address
            info.phone           = phone
            info.email           = email
            info.office_hours    = office_hours
            info.facebook_url    = facebook_url
            info.instagram_url   = instagram_url
            info.whatsapp_number = whatsapp_number
            info.map_embed_url   = map_embed_url
            info.save()
            messages.success(request, 'Contact information updated successfully.')
            return redirect('dashboard:edit_contact_info')

    else:
        form_data = {
            'address':         info.address,
            'phone':           info.phone,
            'email':           info.email,
            'office_hours':    info.office_hours,
            'facebook_url':    info.facebook_url,
            'instagram_url':   info.instagram_url,
            'whatsapp_number': info.whatsapp_number,
            'map_embed_url':   info.map_embed_url,
        }

    context = {
        'page_title': 'Edit Contact Info',
        'info':       info,
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_contact_info.html', context)


# ======================================================================
# Core Values Management  (super-admin only)
# ======================================================================

@super_admin_required
def manage_core_values(request):
    """Lists all CoreValue records ordered by display order."""
    values = CoreValue.objects.order_by('order', 'title')
    context = {
        'page_title': 'Core Values',
        'values':     values,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_core_values.html', context)


@super_admin_required
def add_core_value(request):
    """GET — blank form.  POST — create CoreValue, redirect."""
    errors    = {}
    form_data = {'title': '', 'description': '', 'icon': 'fas fa-star', 'order': '0'}

    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        icon        = request.POST.get('icon', 'fas fa-star').strip() or 'fas fa-star'
        order_raw   = request.POST.get('order', '0').strip()

        if not title:
            errors['title'] = 'Title is required.'
        if not description:
            errors['description'] = 'Description is required.'

        order = 0
        try:
            order = int(order_raw)
        except ValueError:
            errors['order'] = 'Order must be a whole number.'

        form_data = {
            'title': title, 'description': description,
            'icon': icon, 'order': order_raw,
        }

        if not errors:
            CoreValue.objects.create(
                title=title, description=description,
                icon=icon, order=order,
            )
            messages.success(request, f'Core value "{title}" added successfully.')
            return redirect('dashboard:manage_core_values')

    context = {
        'page_title': 'Add Core Value',
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_core_value.html', context)


@super_admin_required
def edit_core_value(request, pk):
    """GET — pre-filled form.  POST — save changes, redirect."""
    value  = get_object_or_404(CoreValue, pk=pk)
    errors = {}

    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        icon        = request.POST.get('icon', 'fas fa-star').strip() or 'fas fa-star'
        order_raw   = request.POST.get('order', '0').strip()

        if not title:
            errors['title'] = 'Title is required.'
        if not description:
            errors['description'] = 'Description is required.'

        order = value.order
        try:
            order = int(order_raw)
        except ValueError:
            errors['order'] = 'Order must be a whole number.'

        form_data = {
            'title': title, 'description': description,
            'icon': icon, 'order': order_raw,
        }

        if not errors:
            value.title       = title
            value.description = description
            value.icon        = icon
            value.order       = order
            value.save()
            messages.success(request, f'Core value "{title}" updated.')
            return redirect('dashboard:manage_core_values')
    else:
        form_data = {
            'title':       value.title,
            'description': value.description,
            'icon':        value.icon,
            'order':       value.order,
        }

    context = {
        'page_title': f'Edit — {value.title}',
        'value':      value,
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_core_value.html', context)


@super_admin_required
def delete_core_value(request, pk):
    """POST-only.  Deletes the CoreValue and redirects."""
    if request.method == 'POST':
        value = get_object_or_404(CoreValue, pk=pk)
        title = value.title
        value.delete()
        messages.success(request, f'Core value "{title}" deleted.')
    return redirect('dashboard:manage_core_values')


# ======================================================================
# Leadership Profiles Management  (super-admin only)
# ======================================================================

@super_admin_required
def manage_leadership(request):
    """Lists all LeadershipProfile records ordered by display order."""
    leaders = LeadershipProfile.objects.order_by('order', 'name')
    context = {
        'page_title': 'Leadership Profiles',
        'leaders':    leaders,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/manage_leadership.html', context)


@super_admin_required
def add_leader(request):
    """GET — blank form.  POST — create LeadershipProfile, redirect."""
    errors    = {}
    form_data = {
        'name': '', 'role': '', 'bio': '', 'email': '',
        'phone': '', 'order': '0', 'is_active': True,
    }

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        role      = request.POST.get('role', '').strip()
        bio       = request.POST.get('bio', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        order_raw = request.POST.get('order', '0').strip()
        is_active = 'is_active' in request.POST

        if not name:
            errors['name'] = 'Full name is required.'
        if not role:
            errors['role'] = 'Role / title is required.'

        order = 0
        try:
            order = int(order_raw)
        except ValueError:
            errors['order'] = 'Order must be a whole number.'

        form_data = {
            'name': name, 'role': role, 'bio': bio,
            'email': email, 'phone': phone,
            'order': order_raw, 'is_active': is_active,
        }

        if not errors:
            leader = LeadershipProfile.objects.create(
                name=name, role=role, bio=bio,
                email=email, phone=phone,
                order=order, is_active=is_active,
            )
            if request.FILES.get('photo'):
                leader.photo = request.FILES['photo']
                leader.save(update_fields=['photo'])
            messages.success(request, f'"{name}" added to leadership profiles.')
            return redirect('dashboard:manage_leadership')

    context = {
        'page_title': 'Add Leader',
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/add_leader.html', context)


@super_admin_required
def edit_leader(request, pk):
    """GET — pre-filled form with photo preview.  POST — save changes."""
    leader = get_object_or_404(LeadershipProfile, pk=pk)
    errors = {}

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        role      = request.POST.get('role', '').strip()
        bio       = request.POST.get('bio', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        order_raw = request.POST.get('order', '0').strip()
        is_active = 'is_active' in request.POST

        if not name:
            errors['name'] = 'Full name is required.'
        if not role:
            errors['role'] = 'Role / title is required.'

        order = leader.order
        try:
            order = int(order_raw)
        except ValueError:
            errors['order'] = 'Order must be a whole number.'

        form_data = {
            'name': name, 'role': role, 'bio': bio,
            'email': email, 'phone': phone,
            'order': order_raw, 'is_active': is_active,
        }

        if not errors:
            leader.name      = name
            leader.role      = role
            leader.bio       = bio
            leader.email     = email
            leader.phone     = phone
            leader.order     = order
            leader.is_active = is_active
            leader.save()
            if request.FILES.get('photo'):
                leader.photo = request.FILES['photo']
                leader.save(update_fields=['photo'])
            messages.success(request, f'"{name}" updated successfully.')
            return redirect('dashboard:manage_leadership')
    else:
        form_data = {
            'name':      leader.name,
            'role':      leader.role,
            'bio':       leader.bio,
            'email':     leader.email,
            'phone':     leader.phone,
            'order':     leader.order,
            'is_active': leader.is_active,
        }

    context = {
        'page_title': f'Edit — {leader.name}',
        'leader':     leader,
        'form_data':  form_data,
        'errors':     errors,
        **_sidebar_counts(),
    }
    return render(request, 'dashboard/edit_leader.html', context)


@super_admin_required
def delete_leader(request, pk):
    """POST-only.  Deletes the LeadershipProfile and redirects."""
    if request.method == 'POST':
        leader = get_object_or_404(LeadershipProfile, pk=pk)
        name   = leader.name
        leader.delete()
        messages.success(request, f'"{name}" removed from leadership profiles.')
    return redirect('dashboard:manage_leadership')


@super_admin_required
def toggle_leader(request, pk):
    """POST-only.  Flips is_active on a LeadershipProfile."""
    if request.method == 'POST':
        leader = get_object_or_404(LeadershipProfile, pk=pk)
        leader.is_active = not leader.is_active
        leader.save(update_fields=['is_active'])
        verb = 'shown' if leader.is_active else 'hidden'
        messages.success(request, f'"{leader.name}" is now {verb} on the About page.')
    return redirect('dashboard:manage_leadership')
