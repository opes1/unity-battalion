from django.contrib import admin

from .models import Company, CompanyUpdateRequest


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Company model.
    Provides rich filtering and search so council staff can quickly
    find and manage any of the battalion's companies.
    """

    # ------------------------------------------------------------------
    # List view columns
    # ------------------------------------------------------------------
    list_display = (
        'name',
        'church',
        'location',
        'meeting_day',
        'meeting_time',
        'is_active',
        'date_established',
        'created_at',
    )

    # ------------------------------------------------------------------
    # Sidebar filters
    # ------------------------------------------------------------------
    list_filter = (
        'is_active',
        'meeting_day',
    )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    search_fields = (
        'name',
        'church',
        'location',
    )

    # ------------------------------------------------------------------
    # Default sort order — alphabetical by name
    # ------------------------------------------------------------------
    ordering = ('name',)

    # ------------------------------------------------------------------
    # Read-only fields — managed automatically, should not be edited
    # ------------------------------------------------------------------
    readonly_fields = ('created_at', 'updated_at')

    # ------------------------------------------------------------------
    # Detail view fieldsets
    # ------------------------------------------------------------------
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'church', 'location'),
        }),
        ('Meetings & Sections', {
            'fields': ('meeting_day', 'meeting_time', 'sections_offered'),
        }),
        ('About', {
            'fields': ('about', 'date_established'),
        }),
        ('Contact Details', {
            'fields': ('phone', 'email'),
            'description': 'Public contact details shown on the company profile page.',
        }),
        ('Map Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'Decimal-degree GPS coordinates. Set these to show the company as a pin on the interactive map.',
        }),
        ('Media', {
            'fields': ('logo', 'banner'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),   # collapsed by default — less clutter
        }),
    )


@admin.register(CompanyUpdateRequest)
class CompanyUpdateRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for CompanyUpdateRequest.
    Super admins use this view to review, approve, or reject change
    requests submitted by company admins.
    """

    list_display = (
        'company',
        'requested_by',
        'status',
        'requested_at',
        'reviewed_by',
        'reviewed_at',
    )

    list_filter = (
        'status',
        'company',
    )

    search_fields = (
        'company__name',
        'requested_by__username',
        'requested_by__email',
    )

    ordering = ('-requested_at',)

    readonly_fields = ('requested_at',)

    fieldsets = (
        ('Request', {
            'fields': ('company', 'requested_by', 'proposed_data', 'requested_at'),
        }),
        ('Review', {
            'fields': ('status', 'rejection_reason', 'reviewed_by', 'reviewed_at'),
        }),
    )
