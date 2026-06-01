from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.

    Extends Django's built-in UserAdmin so all the standard
    authentication behaviour (password hashing, permission management,
    group assignment) is inherited automatically. We add our custom
    fields (role, company, is_approved, phone, profile_photo) on top.
    """

    # ------------------------------------------------------------------
    # List view — columns shown in the user table
    # ------------------------------------------------------------------
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'company',
        'is_approved',
        'is_active',
        'is_staff',
        'date_joined',
    )

    # ------------------------------------------------------------------
    # Sidebar filters in the list view
    # ------------------------------------------------------------------
    list_filter = (
        'role',
        'is_approved',
        'is_active',
        'is_staff',
        'company',
    )

    # ------------------------------------------------------------------
    # Search — fields Django will query when you type in the search box
    # ------------------------------------------------------------------
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
    )

    # ------------------------------------------------------------------
    # Default column for ordering the list
    # ------------------------------------------------------------------
    ordering = ('last_name', 'first_name')

    # ------------------------------------------------------------------
    # Detail/edit view — fieldsets organise fields into collapsible
    # sections. We extend the base fieldsets with our custom fields.
    # ------------------------------------------------------------------
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BB Profile', {
            'fields': ('role', 'company', 'is_approved', 'phone', 'profile_photo'),
        }),
    )

    # ------------------------------------------------------------------
    # Add-user form — same extra fields shown when creating a new user
    # ------------------------------------------------------------------
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('BB Profile', {
            'fields': ('role', 'company', 'is_approved', 'phone', 'profile_photo'),
        }),
    )
