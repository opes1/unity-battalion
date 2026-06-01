from django.contrib import admin

from .models import BattalionInfo, CoreValue, LeadershipProfile, ContactInfo, ContactMessage


# ======================================================================
# BattalionInfo  —  Singleton admin
# ======================================================================

@admin.register(BattalionInfo)
class BattalionInfoAdmin(admin.ModelAdmin):
    """
    Admin for the BattalionInfo singleton.

    Restrictions:
      • Adding is blocked once a record exists (only one row allowed).
      • Deleting is always blocked — the record should always exist.
    """

    list_display  = ('__str__', 'founded_year', 'headquarters', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Core Identity', {
            'fields': ('founded_year', 'headquarters'),
        }),
        ('Official BB Object Statement', {
            'fields': ('bb_object',),
            'description': (
                'The official, unchanged Boys\' Brigade Object. '
                'Paste the standard text here.'
            ),
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision'),
        }),
        ('History', {
            'fields': ('history',),
        }),
        ('Meta', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Only allow creating the record if none exists yet."""
        return not BattalionInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Never allow deleting the singleton — just edit it."""
        return False


# ======================================================================
# CoreValue
# ======================================================================

@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    """
    Admin for the Core Values grid on the About page.
    The `order` field is editable directly from the list view so
    admins can rearrange values without opening each one individually.
    """

    list_display  = ('title', 'icon', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    ordering      = ('order', 'title')

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'icon', 'order'),
            'description': (
                'Icon must be a valid Font Awesome 6 class string, '
                'e.g. "fas fa-heart". See fontawesome.com/icons for options.'
            ),
        }),
    )


# ======================================================================
# LeadershipProfile
# ======================================================================

@admin.register(LeadershipProfile)
class LeadershipProfileAdmin(admin.ModelAdmin):
    """
    Admin for the leadership team section on the About page.
    `order` and `is_active` are editable from the list view for
    quick rearranging and hiding profiles.
    """

    list_display  = ('name', 'role', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter   = ('is_active',)
    search_fields = ('name', 'role', 'bio')
    ordering      = ('order', 'name')

    fieldsets = (
        ('Identity', {
            'fields': ('name', 'role', 'photo', 'order', 'is_active'),
        }),
        ('Profile Content', {
            'fields': ('bio',),
        }),
        ('Contact Details', {
            'fields': ('email', 'phone'),
            'description': 'These are shown publicly on the About page.',
            'classes': ('collapse',),
        }),
    )


# ======================================================================
# ContactInfo  —  Singleton admin
# ======================================================================

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Admin for the ContactInfo singleton.

    Restrictions:
      • Adding is blocked once a record exists (only one row allowed).
      • Deleting is always blocked — the record should always exist.
    """

    list_display  = ('__str__', 'phone', 'email', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Contact Details', {
            'fields': ('address', 'phone', 'email', 'office_hours'),
            'description': (
                'This information is displayed on the public Contact page '
                'and in the site footer.'
            ),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'whatsapp_number'),
        }),
        ('Map', {
            'fields': ('map_embed_url',),
            'description': (
                'Paste the src URL from Google Maps → Share → Embed a map. '
                'Starts with https://www.google.com/maps/embed?'
            ),
        }),
        ('Meta', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Only allow creating the record if none exists yet."""
        return not ContactInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Never allow deleting the singleton — just edit it."""
        return False


# ======================================================================
# ContactMessage
# ======================================================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin for messages submitted via the public Contact page.

    `is_read` is editable from the list view so admins can mark messages
    as read without opening each one individually.

    Adding new messages from the admin is disabled — messages are created
    only through the public contact form.
    """

    list_display   = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_editable  = ('is_read',)
    list_filter    = ('is_read',)
    search_fields  = ('name', 'email', 'subject', 'message')
    ordering       = ('-created_at',)
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')

    fieldsets = (
        ('Sender', {
            'fields': ('name', 'email', 'phone'),
        }),
        ('Message', {
            'fields': ('subject', 'message'),
        }),
        ('Status', {
            'fields': ('is_read', 'created_at'),
        }),
    )

    def has_add_permission(self, request):
        """Messages are created through the public form, not the admin."""
        return False
