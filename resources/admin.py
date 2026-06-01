from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Resource (downloadable file) model.
    list_editable on is_published lets admins quickly toggle visibility
    for multiple resources from the list view without opening each one.
    """

    # ------------------------------------------------------------------
    # List view columns
    # ------------------------------------------------------------------
    list_display = (
        'title',
        'category',
        'audience',
        'is_published',
        'uploaded_by',
        'uploaded_at',
        'updated_at',
    )

    # ------------------------------------------------------------------
    # Sidebar filters
    # ------------------------------------------------------------------
    list_filter = (
        'category',
        'audience',
        'is_published',
    )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    search_fields = (
        'title',
        'description',
        'uploaded_by__username',
        'uploaded_by__email',
    )

    # ------------------------------------------------------------------
    # Toggle publishing directly from the list view
    # ------------------------------------------------------------------
    list_editable = ('is_published',)

    # ------------------------------------------------------------------
    # Default sort — newest resources first
    # ------------------------------------------------------------------
    ordering = ('-uploaded_at',)

    # ------------------------------------------------------------------
    # Read-only timestamps
    # ------------------------------------------------------------------
    readonly_fields = ('uploaded_at', 'updated_at')

    # ------------------------------------------------------------------
    # Detail view fieldsets
    # ------------------------------------------------------------------
    fieldsets = (
        ('Resource Details', {
            'fields': ('title', 'category', 'description'),
        }),
        ('File & Access', {
            'fields': ('file', 'audience', 'is_published'),
        }),
        ('Attribution', {
            'fields': ('uploaded_by',),
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
