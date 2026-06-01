from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Event model.
    The calendar is one of the most actively managed parts of the site,
    so this view provides rich filtering (by type, company, date) and
    quick-toggle publishing via list_editable.
    """

    # ------------------------------------------------------------------
    # List view columns
    # ------------------------------------------------------------------
    list_display = (
        'title',
        'event_type',
        'date',
        'start_time',
        'end_time',
        'company',
        'location',
        'is_published',
        'created_by',
    )

    # ------------------------------------------------------------------
    # Sidebar filters
    # ------------------------------------------------------------------
    list_filter = (
        'event_type',
        'is_published',
        'company',
        'date',
    )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    search_fields = (
        'title',
        'description',
        'location',
        'company__name',
    )

    # ------------------------------------------------------------------
    # Allow toggling is_published directly from the list view
    # ------------------------------------------------------------------
    list_editable = ('is_published',)

    # ------------------------------------------------------------------
    # Default sort — soonest upcoming events first
    # ------------------------------------------------------------------
    ordering = ('date', 'start_time')

    # ------------------------------------------------------------------
    # Read-only timestamps
    # ------------------------------------------------------------------
    readonly_fields = ('created_at', 'updated_at')

    # ------------------------------------------------------------------
    # Detail view fieldsets
    # ------------------------------------------------------------------
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'event_type', 'description'),
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'location'),
        }),
        ('Scope', {
            'fields': ('company',),
            'description': (
                'Leave "Company" blank for a battalion-wide event '
                'visible to all companies.'
            ),
        }),
        ('Media & Publishing', {
            'fields': ('banner', 'is_published', 'created_by'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
