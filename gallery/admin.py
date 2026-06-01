from django.contrib import admin

from .models import Album, GalleryItem


class GalleryItemInline(admin.TabularInline):
    """
    Inline editor for GalleryItems nested inside the Album detail page.

    This lets admins manage an album and all its photos/videos on one
    screen without navigating away — add items, set captions, and
    reorder them all from the same form.
    """
    model   = GalleryItem
    extra   = 3          # show 3 blank rows ready for new uploads
    fields  = ('media_type', 'file', 'video_url', 'caption', 'order')
    ordering = ('order', 'uploaded_at')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Album model.
    GalleryItems are managed inline so you never need to leave the Album
    page to add or rearrange photos.
    """

    inlines = [GalleryItemInline]

    # ------------------------------------------------------------------
    # List view columns
    # ------------------------------------------------------------------
    list_display = (
        'title',
        'company',
        'event',
        'created_at',
        'updated_at',
    )

    # ------------------------------------------------------------------
    # Sidebar filters
    # ------------------------------------------------------------------
    list_filter = (
        'company',
        'event',
    )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    search_fields = (
        'title',
        'description',
        'company__name',
        'event__title',
    )

    # ------------------------------------------------------------------
    # Default sort — newest albums at the top
    # ------------------------------------------------------------------
    ordering = ('-created_at',)

    # ------------------------------------------------------------------
    # Read-only timestamps
    # ------------------------------------------------------------------
    readonly_fields = ('created_at', 'updated_at')

    # ------------------------------------------------------------------
    # Detail view fieldsets
    # ------------------------------------------------------------------
    fieldsets = (
        ('Album Details', {
            'fields': ('title', 'description'),
        }),
        ('Links', {
            'fields': ('event', 'company'),
            'description': (
                'Link to a specific event or company, or leave both '
                'blank for a battalion-wide album.'
            ),
        }),
        ('Cover Photo', {
            'fields': ('cover_photo',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    """
    Standalone admin for GalleryItem — useful for bulk editing or
    finding a specific item across all albums. Day-to-day management
    is done via the Album inline above.
    """

    list_display = (
        'album',
        'media_type',
        'caption',
        'order',
        'uploaded_at',
    )

    list_filter = (
        'media_type',
        'album',
    )

    search_fields = (
        'caption',
        'album__title',
    )

    ordering = ('album', 'order', 'uploaded_at')
