from django.db import models
from django.conf import settings


class Resource(models.Model):
    """
    A downloadable document or file made available through the site.

    Resources are materials the battalion wants to distribute digitally —
    training handbooks, forms, devotional packs, activity guides, etc.
    Each resource is tagged with a category and an audience so the site
    can show the right materials to the right people.

    Only published resources (is_published=True) are visible on the
    public Resources page. Drafts are accessible in the admin dashboard.
    """

    # ------------------------------------------------------------------
    # Category choices — the broad topic area the resource covers
    # ------------------------------------------------------------------
    class Category(models.TextChoices):
        OFFICERS  = 'officers',  'Officers'   # Officer training, admin forms, manuals
        PARENTS   = 'parents',   'Parents'    # Parent guides, permission slips, FAQs
        BOYS      = 'boys',      'Boys'       # Activity sheets, badge requirements
        GENERAL   = 'general',   'General'    # Council notices, newsletters, policies

    # ------------------------------------------------------------------
    # Audience choices — who the resource is intended for
    # This is separate from category so a "General" notice can still
    # be targeted at "Officers" only if needed.
    # ------------------------------------------------------------------
    class Audience(models.TextChoices):
        OFFICERS  = 'officers',  'Officers'
        PARENTS   = 'parents',   'Parents'
        BOYS      = 'boys',      'Boys'
        ALL       = 'all',       'Everyone'   # Visible to all site visitors

    # ------------------------------------------------------------------
    # title
    # The display name of the resource shown in listings and on the
    # download card, e.g. "BB Officer Training Manual 2024".
    # ------------------------------------------------------------------
    title = models.CharField(max_length=255)

    # ------------------------------------------------------------------
    # category
    # Broad topic grouping used to organise resources into sections on
    # the Resources page (Officers | Parents | Boys | General).
    # ------------------------------------------------------------------
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
    )

    # ------------------------------------------------------------------
    # description
    # A short summary of what the resource contains and who should
    # download it. Shown beneath the title on the resource card.
    # ------------------------------------------------------------------
    description = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # file
    # The actual uploaded document.
    # Accepts any file type (PDF, Word, Excel, etc.) — the admin is
    # responsible for uploading in an appropriate format.
    #   • Saved under  MEDIA_ROOT/resources/
    # null=True / blank=True: a resource can be created as a placeholder
    # before the file is ready, then the file attached later.
    # ------------------------------------------------------------------
    file = models.FileField(
        upload_to='resources/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # audience
    # Controls who can see this resource on the public site.
    #   officers → only logged-in officers
    #   parents  → only logged-in parents (future role)
    #   boys     → only logged-in boys (future role)
    #   all      → visible to every visitor, no login required
    # The view layer enforces this; the field just stores the intent.
    # ------------------------------------------------------------------
    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL,
    )

    # ------------------------------------------------------------------
    # is_published
    # Toggles public visibility of this resource.
    #   False → draft; only visible to admins in the dashboard.
    #   True  → live on the public Resources page.
    # Defaults to False so uploads are reviewed before going live.
    # ------------------------------------------------------------------
    is_published = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # uploaded_at
    # Timestamp set automatically when the resource record is created.
    # Used for "newest first" default ordering and for displaying
    # "Added on <date>" on the resource card.
    # ------------------------------------------------------------------
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # updated_at
    # Refreshed automatically on every save. Useful for knowing when a
    # file was replaced or the description was last edited.
    # ------------------------------------------------------------------
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # uploaded_by  (ForeignKey → accounts.User)
    # Which admin user added this resource. Used for audit purposes.
    # SET_NULL: keep the resource record even if the uploader's account
    # is later deleted.
    # ------------------------------------------------------------------
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_resources',
    )

    def __str__(self):
        return f"{self.title} [{self.get_category_display()}]"

    class Meta:
        verbose_name        = 'Resource'
        verbose_name_plural = 'Resources'
        ordering            = ['-uploaded_at']   # newest resources first
