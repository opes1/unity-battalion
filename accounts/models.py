from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model for Unity Battalion Council.

    Extends Django's built-in AbstractUser so we keep all standard
    authentication fields for free (username, email, password,
    first_name, last_name, is_active, is_staff, date_joined, etc.)
    and bolt on the BB-specific fields below.

    IMPORTANT: AUTH_USER_MODEL = 'accounts.User' must be set in
    settings.py BEFORE the first migration is created. Changing it
    after migrations exist is very painful.
    """

    # ------------------------------------------------------------------
    # Role choices
    # ------------------------------------------------------------------
    class Role(models.TextChoices):
        SUPER_ADMIN   = 'super_admin',   'Super Admin'
        COMPANY_ADMIN = 'company_admin', 'Company Admin'

    # ------------------------------------------------------------------
    # role
    # Determines what the user can see and do across the entire site.
    #   super_admin   → council-level access: can manage ALL companies,
    #                   approve users, edit site-wide settings.
    #   company_admin → scoped access: can only manage their own
    #                   company's members, events, and content.
    # ------------------------------------------------------------------
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COMPANY_ADMIN,
    )

    # ------------------------------------------------------------------
    # company  (ForeignKey → companies.Company)
    # Links this user to a specific BB company, e.g. "1st Unity Company".
    # Rules:
    #   • super_admins have no company → null=True / blank=True.
    #   • company_admins must have one set during approval.
    #   • If a Company record is deleted, the user is kept but their
    #     company field is cleared to NULL (SET_NULL) rather than also
    #     deleting the account.
    # We use the lazy string 'companies.Company' (instead of a direct
    # import) to avoid a circular-import between the two apps.
    # ------------------------------------------------------------------
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admins',   # reverse: my_company.admins.all()
    )

    # ------------------------------------------------------------------
    # is_approved
    # New accounts start as False (pending). A super_admin must flip
    # this to True before the user can log in and access the dashboard.
    # This gives the council a manual vetting step for every sign-up.
    # ------------------------------------------------------------------
    is_approved = models.BooleanField(
        default=False,
    )

    # ------------------------------------------------------------------
    # phone
    # Optional contact number for the user. Stored as plain text so it
    # handles international formats, leading zeros, and extensions freely
    # without needing a specialised phone-number library right now.
    # ------------------------------------------------------------------
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # profile_photo
    # Optional headshot uploaded by (or for) the user.
    #   • Files are saved to  MEDIA_ROOT/profile_photos/<filename>
    #   • null=True  → database column can be NULL when no photo exists
    #   • blank=True → field is not required in Django forms / admin
    # Requires Pillow to be installed:  pip install Pillow
    # ------------------------------------------------------------------
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # Convenience properties
    # Use these in views and templates instead of comparing strings:
    #   {% if user.is_super_admin %} … {% endif %}
    # ------------------------------------------------------------------
    @property
    def is_super_admin(self):
        """True when this user holds the council-level super_admin role."""
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_company_admin(self):
        """True when this user is scoped to a single company."""
        return self.role == self.Role.COMPANY_ADMIN

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------
    def __str__(self):
        full_name = self.get_full_name()
        display   = full_name if full_name.strip() else self.username
        return f"{display} ({self.get_role_display()})"

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['last_name', 'first_name']
