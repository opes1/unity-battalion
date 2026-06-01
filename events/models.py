from django.db import models
from django.conf import settings


class Event(models.Model):
    """
    Represents a single Boys Brigade event on the council calendar.

    Events can be battalion-wide (council-level, e.g. an annual
    competition or church parade) or company-specific (e.g. a local
    fundraiser). The distinction is made via the `company` field:
    a NULL company means the event belongs to the whole battalion.

    Only published events (is_published=True) are shown to the public.
    Super admins publish battalion-wide events; company admins can
    publish events scoped to their own company.
    """

    # ------------------------------------------------------------------
    # Event type choices
    # ------------------------------------------------------------------
    class EventType(models.TextChoices):
        PARADE      = 'parade',      'Parade'       # Formal BB parade/inspection
        COMPETITION = 'competition', 'Competition'  # Inter-company or external contest
        TRAINING    = 'training',    'Training'     # Officer or boys training session
        CHURCH      = 'church',      'Church'       # Church parade or service
        OTHER       = 'other',       'Other'        # Catch-all for miscellaneous events

    # ------------------------------------------------------------------
    # title
    # Short, descriptive name for the event shown in listings and cards,
    # e.g. "Annual Battalion Inspection 2025".
    # ------------------------------------------------------------------
    title = models.CharField(max_length=255)

    # ------------------------------------------------------------------
    # description
    # Full details about the event — agenda, dress code, what to bring,
    # special instructions, etc. Displayed on the event detail page.
    # ------------------------------------------------------------------
    description = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # event_type
    # Categorises the event so the calendar can colour-code or filter by
    # type. Stored as a short text key (e.g. 'parade').
    # ------------------------------------------------------------------
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
    )

    # ------------------------------------------------------------------
    # date
    # The calendar date on which the event takes place.
    # Stored separately from start_time so date-only lookups are simple:
    #   Event.objects.filter(date__month=12)
    # ------------------------------------------------------------------
    date = models.DateField()

    # ------------------------------------------------------------------
    # start_time / end_time
    # Optional clock times for the event.
    # Both are nullable so an event can be entered as "date only" when
    # the exact time is not yet confirmed.
    # ------------------------------------------------------------------
    start_time = models.TimeField(
        null=True,
        blank=True,
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # location
    # Free-text venue description, e.g. "Unity Baptist Church Hall,
    # 14 Brigade Road, Lagos". Optional — may be TBC at creation time.
    # ------------------------------------------------------------------
    location = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # company  (ForeignKey → companies.Company, nullable)
    # Scopes the event to a single company when set.
    # NULL → battalion-wide event visible to everyone.
    # SET_NULL: if the company is deleted, keep the event record but
    # promote it to battalion-wide by clearing this field.
    # ------------------------------------------------------------------
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',   # company.events.all()
        # Leave blank for council-level events that span all companies.
    )

    # ------------------------------------------------------------------
    # banner
    # Optional wide promotional image for the event, shown at the top
    # of the event detail page and in featured cards.
    #   • Saved under  MEDIA_ROOT/event_banners/
    # ------------------------------------------------------------------
    banner = models.ImageField(
        upload_to='event_banners/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # is_published
    # Controls whether the event is visible to the public.
    #   False → draft/internal; only visible to admins in the dashboard.
    #   True  → live on the public calendar.
    # Defaults to False so new events are drafts until explicitly published.
    # ------------------------------------------------------------------
    is_published = models.BooleanField(default=False)

    # ------------------------------------------------------------------
    # created_by
    # The admin user who created this event record.
    # SET_NULL: keep the event even if the creator's account is deleted.
    # ------------------------------------------------------------------
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events',
    )

    # ------------------------------------------------------------------
    # created_at
    # Timestamp set automatically when the event is first saved.
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # updated_at
    # Refreshed automatically on every save — useful for knowing when
    # event details were last changed.
    # ------------------------------------------------------------------
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def is_battalion_wide(self):
        """True when the event is not scoped to a specific company."""
        return self.company is None

    def __str__(self):
        scope = self.company.name if self.company else 'Battalion'
        return f"{self.title} — {self.date} ({scope})"

    class Meta:
        verbose_name        = 'Event'
        verbose_name_plural = 'Events'
        ordering            = ['date', 'start_time']
