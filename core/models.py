from django.db import models


# ======================================================================
# BattalionInfo  —  Singleton record (only one row ever exists)
# ======================================================================

class BattalionInfo(models.Model):
    """
    Stores the battalion's key descriptive content for the About page.

    Singleton pattern: only one row should ever exist (pk always = 1).
    Use  BattalionInfo.get_solo()  to fetch it safely — the record is
    created with sensible defaults on first access if it doesn't exist.

    Super admins edit this through the Django admin panel.
    """

    # ------------------------------------------------------------------
    # history
    # A narrative about how the battalion was founded and has grown.
    # Displayed as the main body text in the "Our History" section.
    # ------------------------------------------------------------------
    history = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # mission
    # One or two sentences stating what the battalion actively does
    # today, e.g. "To nurture disciplined, Christ-centred young men…"
    # ------------------------------------------------------------------
    mission = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # vision
    # A forward-looking statement about what the battalion aspires to
    # become or achieve, e.g. "A battalion where every boy …"
    # ------------------------------------------------------------------
    vision = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # bb_object
    # The official, unchanged Boys' Brigade Object statement:
    # "The advancement of Christ's Kingdom among Boys and the promotion
    #  of habits of Obedience, Reverence, Discipline, Self-Respect and
    #  all that tends towards a true Christian manliness."
    # Stored separately so it can be highlighted distinctly on the page.
    # ------------------------------------------------------------------
    bb_object = models.TextField(
        blank=True,
        default='',
        verbose_name='BB Object Statement',
    )

    # ------------------------------------------------------------------
    # founded_year
    # The four-digit year the battalion (not the global BB) was founded.
    # Optional — shown as "Established <year>" on the About page.
    # ------------------------------------------------------------------
    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Four-digit year the battalion was established, e.g. 1985.',
    )

    # ------------------------------------------------------------------
    # headquarters
    # Short text address or location of the council headquarters,
    # e.g. "Lagos, Nigeria". Shown in the history / contact section.
    # ------------------------------------------------------------------
    headquarters = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # Identity fields
    # Core branding strings displayed across the public site.
    # ------------------------------------------------------------------
    name = models.CharField(
        max_length=200,
        blank=True,
        default='Unity Battalion Council',
        help_text='Full name of the battalion council.',
    )
    motto = models.CharField(
        max_length=200,
        blank=True,
        default='Sure and Stedfast',
        help_text='Official motto, e.g. "Sure and Stedfast".',
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        default='Boys Brigade Council',
        help_text='Short subtitle shown beneath the name, e.g. "Boys Brigade Council".',
    )
    organisation = models.CharField(
        max_length=200,
        blank=True,
        default="Boys' Brigade Nigeria",
        help_text='Parent organisation name, e.g. "Boys\' Brigade Nigeria".',
    )
    age_range = models.CharField(
        max_length=100,
        blank=True,
        default='Boys aged 5 – 18+',
        help_text='Age range of members, e.g. "Boys aged 5 – 18+".',
    )

    # ------------------------------------------------------------------
    # Stats
    # Headline numbers shown in the stats strip on the About and Home pages.
    # Stored as strings so the admin can include the "+" suffix freely.
    # ------------------------------------------------------------------
    active_companies = models.CharField(
        max_length=20,
        blank=True,
        default='12+',
        help_text='e.g. "12+" — shown in the stats strip.',
    )
    boys_enrolled = models.CharField(
        max_length=20,
        blank=True,
        default='200+',
        help_text='e.g. "200+" — shown in the stats strip.',
    )
    bb_sections = models.CharField(
        max_length=20,
        blank=True,
        default='4',
        help_text='Number of BB sections offered.',
    )

    # ------------------------------------------------------------------
    # Page headings / CTA copy
    # Editable labels for key sections of the About page.
    # ------------------------------------------------------------------
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        default='About Unity Battalion',
        help_text='H1 heading on the About page hero banner.',
    )
    history_heading = models.CharField(
        max_length=200,
        blank=True,
        default='A Legacy of Faith & Service',
        help_text='H2 heading for the History section.',
    )
    cta_heading = models.CharField(
        max_length=200,
        blank=True,
        default='Get Involved with the Battalion',
        help_text='Heading for the bottom call-to-action section.',
    )
    cta_text = models.TextField(
        blank=True,
        default=(
            'Whether you want to enrol your son, start a new company in your church, '
            'or volunteer as an officer, we would love to hear from you.'
        ),
        help_text='Paragraph text beneath the CTA heading.',
    )

    # ------------------------------------------------------------------
    # banner
    # Optional hero/banner image for the About page.
    # ------------------------------------------------------------------
    banner = models.ImageField(
        upload_to='battalion/',
        null=True,
        blank=True,
        help_text='Optional banner/hero image for the About page.',
    )

    # ------------------------------------------------------------------
    # Home page specific content
    # Fields that control the home page only (not the About page).
    # ------------------------------------------------------------------
    home_hero_title = models.TextField(
        blank=True,
        default='Building Boys of Character, Faith & Service',
        help_text='Main H1 heading on the home page hero section.',
    )
    home_hero_description = models.TextField(
        blank=True,
        default=(
            "Unity Battalion Council is committed to advancing Christ's Kingdom "
            "among boys, nurturing obedience, reverence, discipline, self-respect "
            "and all that tends towards a true Christian manliness."
        ),
        help_text='Short paragraph beneath the hero heading on the home page.',
    )
    years_of_service = models.CharField(
        max_length=20,
        blank=True,
        default='10+',
        help_text='e.g. "10+" — shown as the "Years of Service" stat on the home page.',
    )
    home_cta_heading = models.TextField(
        blank=True,
        default='Ready to Join the Battalion?',
        help_text='Heading for the CTA banner at the bottom of the home page.',
    )
    home_cta_text = models.TextField(
        blank=True,
        default=(
            "Whether you're a parent looking for the right programme for your boy, "
            "or a church wanting to start a company, we'd love to hear from you."
        ),
        help_text='Paragraph text beneath the home page CTA heading.',
    )
    gallery_subtitle = models.TextField(
        blank=True,
        default=(
            'A glimpse into the life of Unity Battalion: parades, competitions, '
            'training camps, and community service captured in pictures.'
        ),
        help_text='Subtitle for the gallery preview section on the home page.',
    )

    # ------------------------------------------------------------------
    # updated_at
    # Refreshed automatically whenever a super admin saves this record.
    # ------------------------------------------------------------------
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Singleton helpers
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """Force pk=1 so there can only ever be one BattalionInfo row."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Fetch the singleton record, creating it with empty defaults if
        it doesn't exist yet. Safe to call from any view.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Battalion Information'

    class Meta:
        verbose_name        = 'Battalion Information'
        verbose_name_plural = 'Battalion Information'


# ======================================================================
# CoreValue  —  One card per value in the "Our Values" grid
# ======================================================================

class CoreValue(models.Model):
    """
    Represents a single core value of the battalion, displayed as a
    card in the values grid on the About page.

    Examples:
      title="Obedience", icon="fas fa-check-circle", order=1
      title="Reverence",  icon="fas fa-pray",        order=2
    """

    # ------------------------------------------------------------------
    # title
    # The value name, e.g. "Obedience", "Discipline", "Self-Respect".
    # Shown as the card heading.
    # ------------------------------------------------------------------
    title = models.CharField(max_length=100)

    # ------------------------------------------------------------------
    # description
    # One or two sentences explaining what this value means in the
    # context of the battalion and BB programme.
    # ------------------------------------------------------------------
    description = models.TextField()

    # ------------------------------------------------------------------
    # icon
    # A Font Awesome 6 icon class string, e.g. "fas fa-shield-alt".
    # Rendered directly in the template: <i class="{{ value.icon }}"></i>
    # The admin help_text lists common sensible options.
    # ------------------------------------------------------------------
    icon = models.CharField(
        max_length=80,
        default='fas fa-star',
        help_text=(
            'Font Awesome class, e.g. "fas fa-heart", "fas fa-shield-alt", '
            '"fas fa-pray", "fas fa-users", "fas fa-bible".'
        ),
    )

    # ------------------------------------------------------------------
    # order
    # Controls the left-to-right, top-to-bottom display order on the
    # values grid. Lower numbers appear first.
    # ------------------------------------------------------------------
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Lower numbers appear first in the values grid.',
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name        = 'Core Value'
        verbose_name_plural = 'Core Values'
        ordering            = ['order', 'title']


# ======================================================================
# LeadershipProfile  —  One card per leader in the "Our Team" section
# ======================================================================

class LeadershipProfile(models.Model):
    """
    Represents a single member of the battalion's leadership team,
    displayed as a profile card on the About page.

    Examples: Battalion President, Secretary, Chaplain, Treasurer.
    """

    # ------------------------------------------------------------------
    # name
    # Full name of the leader, e.g. "Rev. John Adeyemi".
    # ------------------------------------------------------------------
    name = models.CharField(max_length=150)

    # ------------------------------------------------------------------
    # role
    # Their official title in the battalion,
    # e.g. "Battalion President", "Honorary Secretary".
    # ------------------------------------------------------------------
    role = models.CharField(max_length=150)

    # ------------------------------------------------------------------
    # photo
    # Optional headshot. Displayed as the card's profile image.
    #   • Saved under  MEDIA_ROOT/leadership/
    # If absent, the template shows an icon placeholder.
    # ------------------------------------------------------------------
    photo = models.ImageField(
        upload_to='leadership/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # bio
    # A short paragraph about this person — background, years of
    # service, areas of responsibility, etc.
    # ------------------------------------------------------------------
    bio = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # email / phone
    # Optional public contact details shown on the profile card.
    # ------------------------------------------------------------------
    email = models.EmailField(
        blank=True,
        default='',
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # order
    # Controls the left-to-right, top-to-bottom display sequence.
    # The Battalion President is typically order=1.
    # ------------------------------------------------------------------
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Lower numbers appear first. Set 1 for the President.',
    )

    # ------------------------------------------------------------------
    # is_active
    # Toggle to hide a profile without deleting the record — useful
    # when a leader steps down but their record should be kept.
    # ------------------------------------------------------------------
    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this profile from the public About page.',
    )

    def __str__(self):
        return f"{self.name} — {self.role}"

    class Meta:
        verbose_name        = 'Leadership Profile'
        verbose_name_plural = 'Leadership Profiles'
        ordering            = ['order', 'name']


# ======================================================================
# ContactInfo  —  Singleton record for the Contact page
# ======================================================================

class ContactInfo(models.Model):
    """
    Stores the battalion's public contact details for the Contact page.

    Singleton pattern: only one row should ever exist (pk always = 1).
    Use  ContactInfo.get_solo()  to fetch it safely — the record is
    created with blank defaults on first access if it doesn't exist yet.

    Super admins edit this through the Django admin panel.
    """

    # ------------------------------------------------------------------
    # address
    # Full postal/physical address of the battalion headquarters.
    # Displayed in the contact sidebar and footer.
    # ------------------------------------------------------------------
    address = models.TextField(
        blank=True,
        default='',
        help_text='Full postal address of the battalion headquarters.',
    )

    # ------------------------------------------------------------------
    # phone
    # Primary contact phone number, including country code.
    # e.g. "+234 800 000 0000"
    # ------------------------------------------------------------------
    phone = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='Include country code, e.g. +234 800 000 0000',
    )

    # ------------------------------------------------------------------
    # email
    # Primary contact email address, e.g. info@unitybattalion.org
    # ------------------------------------------------------------------
    email = models.EmailField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # office_hours
    # Short text describing when the office is open.
    # e.g. "Mon – Fri: 9am – 5pm"
    # ------------------------------------------------------------------
    office_hours = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text='e.g. "Mon – Fri: 9am – 5pm"',
    )

    # ------------------------------------------------------------------
    # facebook_url / instagram_url
    # Full URL to the battalion's social media profiles.
    # ------------------------------------------------------------------
    facebook_url = models.URLField(
        blank=True,
        default='',
        verbose_name='Facebook URL',
    )
    instagram_url = models.URLField(
        blank=True,
        default='',
        verbose_name='Instagram URL',
    )

    # ------------------------------------------------------------------
    # whatsapp_number
    # WhatsApp contact number — used to build a wa.me deep link.
    # Include country code without leading +, e.g. "2348000000000"
    # ------------------------------------------------------------------
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text='Digits only, no + prefix, e.g. 2348000000000',
        verbose_name='WhatsApp Number',
    )

    # ------------------------------------------------------------------
    # map_embed_url
    # Google Maps embed URL from Share → Embed a map → src="..."
    # Rendered inside an <iframe> on the contact page.
    # ------------------------------------------------------------------
    map_embed_url = models.URLField(
        blank=True,
        default='',
        verbose_name='Google Maps Embed URL',
        help_text=(
            'Paste the src URL from Google Maps → Share → Embed a map. '
            'Starts with https://www.google.com/maps/embed?'
        ),
    )

    # ------------------------------------------------------------------
    # updated_at
    # ------------------------------------------------------------------
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------
    # Singleton helpers
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        """Force pk=1 so there can only ever be one ContactInfo row."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Fetch the singleton record, creating it with blank defaults if
        it doesn't exist yet.  Safe to call from any view.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Contact Information'

    class Meta:
        verbose_name        = 'Contact Information'
        verbose_name_plural = 'Contact Information'


# ======================================================================
# ContactMessage  —  Submitted enquiries from the Contact page
# ======================================================================

class ContactMessage(models.Model):
    """
    Stores a single message submitted through the public Contact page.

    Messages are created by the contact view on successful POST.
    Admins read and manage them through the Django admin panel —
    the `is_read` flag lets them track which messages have been handled.
    """

    # ------------------------------------------------------------------
    # name / email / phone
    # The sender's contact details as entered on the form.
    # phone is optional.
    # ------------------------------------------------------------------
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(
        max_length=30,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # subject / message
    # The subject line and body of the enquiry.
    # ------------------------------------------------------------------
    subject = models.CharField(max_length=255)
    message = models.TextField()

    # ------------------------------------------------------------------
    # created_at
    # Timestamp set automatically when the message is submitted.
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # is_read
    # Toggled by admins once the message has been read / actioned.
    # Defaults to False so new messages stand out in the admin list.
    # ------------------------------------------------------------------
    is_read = models.BooleanField(
        default=False,
        help_text='Mark as read once the message has been actioned.',
    )

    def __str__(self):
        return f"{self.name} — {self.subject}"

    class Meta:
        verbose_name        = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering            = ['-created_at']   # newest messages first
