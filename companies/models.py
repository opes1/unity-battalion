from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Represents a single Boys Brigade company affiliated with
    Unity Battalion Council.

    A "company" in BB is the local unit — it belongs to a church,
    meets on a specific day, and runs one or more BB sections
    (age groups). Each company is managed by one or more
    company_admin users from the accounts app.
    """

    # ------------------------------------------------------------------
    # Meeting day choices — Monday through Sunday
    # ------------------------------------------------------------------
    class MeetingDay(models.TextChoices):
        MONDAY    = 'MON', 'Monday'
        TUESDAY   = 'TUE', 'Tuesday'
        WEDNESDAY = 'WED', 'Wednesday'
        THURSDAY  = 'THU', 'Thursday'
        FRIDAY    = 'FRI', 'Friday'
        SATURDAY  = 'SAT', 'Saturday'
        SUNDAY    = 'SUN', 'Sunday'

    # ------------------------------------------------------------------
    # BB section choices — the four official age-group divisions
    # These are stored as JSON in sections_offered (see below).
    # ------------------------------------------------------------------
    class Section(models.TextChoices):
        ANCHOR_BOYS = 'anchor_boys', 'Anchor Boys'    # Ages  5 – 8
        JUNIORS     = 'juniors',     'Juniors'         # Ages  8 – 11
        COMPANY     = 'company',     'Company Section' # Ages 11 – 15
        SENIORS     = 'seniors',     'Seniors'         # Ages 15 – 18+

    # ------------------------------------------------------------------
    # name
    # The official name of the company, e.g. "1st Unity Company".
    # ------------------------------------------------------------------
    name = models.CharField(max_length=200)

    # ------------------------------------------------------------------
    # church
    # The church or sponsoring body the company is attached to,
    # e.g. "Unity Baptist Church". BB companies in Nigeria are almost
    # always church-based.
    # ------------------------------------------------------------------
    church = models.CharField(max_length=200)

    # ------------------------------------------------------------------
    # location
    # Free-text physical address of the company's meeting venue.
    # Stored as text so it can handle long Nigerian addresses without
    # hitting a character limit.
    # ------------------------------------------------------------------
    location = models.TextField()

    # ------------------------------------------------------------------
    # meeting_day
    # The day of the week the company holds its regular parade.
    # Stored as a 3-character abbreviation (MON, TUE, …) so it is
    # compact in the database, but displayed with the full name in forms.
    # ------------------------------------------------------------------
    meeting_day = models.CharField(
        max_length=3,
        choices=MeetingDay.choices,
    )

    # ------------------------------------------------------------------
    # meeting_time
    # The clock time the parade starts, e.g. 17:00.
    # Stored as a Django TimeField — renders as HH:MM in templates.
    # ------------------------------------------------------------------
    meeting_time = models.TimeField()

    # ------------------------------------------------------------------
    # sections_offered
    # Which BB age-group sections this company runs.
    # Stored as a JSON list of Section keys, e.g.:
    #   ["anchor_boys", "juniors", "company"]
    # Valid values are defined in the Section inner class above.
    # Using JSONField keeps this as a single column while allowing
    # a variable-length set of selections per company.
    # ------------------------------------------------------------------
    sections_offered = models.JSONField(
        default=list,   # empty list when no sections chosen yet
        blank=True,
    )

    # ------------------------------------------------------------------
    # about
    # A free-text description of the company — its history, ethos,
    # achievements, or anything the admin wants the public to know.
    # Optional; defaults to an empty string so the column is never NULL.
    # ------------------------------------------------------------------
    about = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # logo
    # The company's official logo image.
    #   • Saved under  MEDIA_ROOT/company_logos/
    #   • null=True  → no logo uploaded yet (DB column can be NULL)
    #   • blank=True → optional in forms and admin
    # ------------------------------------------------------------------
    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # banner
    # A wide hero/cover image shown at the top of the company's
    # public profile page.
    #   • Saved under  MEDIA_ROOT/company_banners/
    # ------------------------------------------------------------------
    banner = models.ImageField(
        upload_to='company_banners/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # is_active
    # Whether the company is currently operational.
    #   True  → shown in public listings, accessible to its admins.
    #   False → hidden from the public; a super_admin can reactivate it.
    # Defaults to True so newly created companies are live immediately.
    # ------------------------------------------------------------------
    is_active = models.BooleanField(default=True)

    # ------------------------------------------------------------------
    # date_established
    # The calendar date the company was founded, if known.
    # Optional — older companies may not have an exact record.
    # ------------------------------------------------------------------
    date_established = models.DateField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # latitude / longitude
    # Optional GPS coordinates for the company's meeting venue.
    # When set, the company will appear as a pin on the public map.
    # Enter decimal degrees, e.g. 6.4550 / 3.3841 (Lagos).
    # Leave null if the exact coordinates are not yet known.
    # ------------------------------------------------------------------
    latitude = models.FloatField(
        null=True,
        blank=True,
        help_text='Decimal degrees, e.g. 6.4550',
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        help_text='Decimal degrees, e.g. 3.3841',
    )

    # ------------------------------------------------------------------
    # phone / email
    # Optional public contact details shown on the company profile page.
    # ------------------------------------------------------------------
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')

    # ------------------------------------------------------------------
    # created_at / updated_at  — audit timestamps
    # created_at: set automatically when the record is first saved;
    #             never changes after that (auto_now_add=True).
    # updated_at: refreshed automatically every time the record is
    #             saved, giving a reliable "last modified" marker.
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Helper: human-readable list of sections for templates
    # Usage:  {{ company.sections_display }}
    # ------------------------------------------------------------------
    @property
    def sections_display(self):
        """
        Returns the human-readable labels for all sections this company
        offers, e.g. ['Anchor Boys', 'Juniors'].
        Looks up each stored key against the Section choices.
        """
        label_map = dict(self.Section.choices)
        return [label_map[s] for s in self.sections_offered if s in label_map]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name        = 'Company'
        verbose_name_plural = 'Companies'
        ordering            = ['name']


# ======================================================================
# CompanyUpdateRequest
# ======================================================================

class CompanyUpdateRequest(models.Model):
    """
    Tracks change requests submitted by company admins.

    Company admins cannot edit their company profile directly — instead
    they submit a CompanyUpdateRequest containing their proposed changes.
    A super_admin then reviews the request and either approves or
    rejects it, optionally leaving a rejection reason.

    This gives the council oversight of what is published publicly
    without blocking company admins from initiating updates.
    """

    # ------------------------------------------------------------------
    # Status choices for the review workflow
    # ------------------------------------------------------------------
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'   # Awaiting super_admin review
        APPROVED = 'approved', 'Approved'  # Changes accepted and applied
        REJECTED = 'rejected', 'Rejected'  # Changes declined with a reason

    # ------------------------------------------------------------------
    # company
    # Which company this update request is for.
    # CASCADE: if the company is deleted, its pending requests go too —
    # there is nothing left to update.
    # ------------------------------------------------------------------
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='update_requests',  # company.update_requests.all()
    )

    # ------------------------------------------------------------------
    # proposed_data
    # A JSON snapshot of the fields the company admin wants to change,
    # e.g. {"about": "New text...", "meeting_time": "18:00"}.
    # Storing the diff as JSON means we don't need a separate column
    # for every possible field that could be updated.
    # ------------------------------------------------------------------
    proposed_data = models.JSONField(
        default=dict,
        # Keys mirror Company field names; values are the proposed values.
    )

    # ------------------------------------------------------------------
    # requested_by
    # The company admin who submitted this change request.
    # SET_NULL: if the user account is deleted, keep the request for
    # the audit trail but clear the link to the user.
    # ------------------------------------------------------------------
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # resolves to accounts.User
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_update_requests',
    )

    # ------------------------------------------------------------------
    # status
    # Where the request sits in the review workflow.
    # Starts as 'pending' and is moved to 'approved' or 'rejected'
    # by a super_admin.
    # ------------------------------------------------------------------
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # ------------------------------------------------------------------
    # rejection_reason
    # Plain-text explanation from the super_admin if the request is
    # rejected, so the company admin knows what to fix and resubmit.
    # Optional — only required when status = 'rejected'.
    # ------------------------------------------------------------------
    rejection_reason = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # requested_at
    # Timestamp set automatically when the request is first created.
    # Used to show admins how long a request has been waiting.
    # ------------------------------------------------------------------
    requested_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # reviewed_at
    # Timestamp set by the view/signal when a super_admin approves
    # or rejects the request. NULL while the request is still pending.
    # ------------------------------------------------------------------
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # reviewed_by
    # Which super_admin reviewed this request.
    # SET_NULL: preserve the audit record even if the reviewer's account
    # is later deleted.
    # NULL while the request is still pending.
    # ------------------------------------------------------------------
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # resolves to accounts.User
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_update_requests',
    )

    def __str__(self):
        return (
            f"Update request for {self.company} "
            f"— {self.get_status_display()} "
            f"({self.requested_at:%Y-%m-%d})"
        )

    class Meta:
        verbose_name        = 'Company Update Request'
        verbose_name_plural = 'Company Update Requests'
        ordering            = ['-requested_at']   # newest first
