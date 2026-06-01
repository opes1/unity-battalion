from django.db import models


class Album(models.Model):
    """
    A named collection of photos and/or videos.

    Albums group related media together — typically everything from a
    single event (e.g. "Annual Inspection 2025 Photos") or a general
    company album (e.g. "1st Unity Company — Highlights").

    An Album can be optionally tied to:
      • an Event  → media from that specific occasion
      • a Company → media belonging to that company's gallery

    Both FKs are nullable so the council can maintain battalion-wide
    albums not attached to any single company or event.
    """

    # ------------------------------------------------------------------
    # title
    # The display name of the album, shown in the gallery grid.
    # e.g. "Annual Battalion Inspection 2025"
    # ------------------------------------------------------------------
    title = models.CharField(max_length=255)

    # ------------------------------------------------------------------
    # description
    # Optional context about the album — what the occasion was, who
    # participated, any notable achievements, etc.
    # ------------------------------------------------------------------
    description = models.TextField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # event  (ForeignKey → events.Event, nullable)
    # Links this album to a specific event if all the media came from it.
    # SET_NULL: if the event is deleted, the album stays but loses its
    # event link — the media is still valuable on its own.
    # ------------------------------------------------------------------
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albums',   # event.albums.all()
    )

    # ------------------------------------------------------------------
    # company  (ForeignKey → companies.Company, nullable)
    # Scopes this album to a specific company's gallery.
    # NULL → battalion-wide album visible to everyone.
    # SET_NULL: keep the album if the company is deleted.
    # ------------------------------------------------------------------
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albums',   # company.albums.all()
    )

    # ------------------------------------------------------------------
    # cover_photo
    # The thumbnail image shown on the album card in the gallery grid.
    # Optional — if not set, the template can fall back to the first
    # GalleryItem in the album.
    #   • Saved under  MEDIA_ROOT/album_covers/
    # ------------------------------------------------------------------
    cover_photo = models.ImageField(
        upload_to='album_covers/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # created_at
    # Set automatically when the album is created. Used for default
    # sort order (newest albums first).
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # updated_at
    # Refreshed on every save — useful for "recently updated" sorting.
    # ------------------------------------------------------------------
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name        = 'Album'
        verbose_name_plural = 'Albums'
        ordering            = ['-created_at']   # newest albums first


# ======================================================================
# GalleryItem
# ======================================================================

class GalleryItem(models.Model):
    """
    A single piece of media (photo or video) inside an Album.

    Each item belongs to exactly one Album. Items are displayed in
    ascending `order` within their album so the admin can control the
    sequence photos appear in (e.g. chronological, or best shots first).

    For photos the `file` field holds the image directly.
    For videos the `file` field holds a video file or a thumbnail,
    and the URL is stored in `video_url` if hosted externally
    (e.g. YouTube). See field comments below.
    """

    # ------------------------------------------------------------------
    # Media type choices
    # ------------------------------------------------------------------
    class MediaType(models.TextChoices):
        PHOTO = 'photo', 'Photo'
        VIDEO = 'video', 'Video'

    # ------------------------------------------------------------------
    # album  (ForeignKey → Album)
    # The album this item belongs to.
    # CASCADE: deleting an album removes all its items — no orphaned
    # media hanging around in the database.
    # ------------------------------------------------------------------
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='items',   # album.items.all()
    )

    # ------------------------------------------------------------------
    # media_type
    # Whether this item is a photo or a video.
    # Drives how the item is rendered in templates:
    #   photo → <img> tag
    #   video → <video> tag or embedded player
    # ------------------------------------------------------------------
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.PHOTO,
    )

    # ------------------------------------------------------------------
    # file
    # The actual uploaded file.
    #   • For photos: the image file (JPEG, PNG, WebP, etc.)
    #   • For videos: either the video file itself, or a still thumbnail
    #     image if the video is hosted externally (see video_url below).
    # Files are saved under  MEDIA_ROOT/gallery/<album_id>/
    # null/blank: a video item might only have a video_url and no
    # local file at all.
    # ------------------------------------------------------------------
    file = models.FileField(
        upload_to='gallery/',
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # video_url
    # Optional external video link (YouTube, Vimeo, etc.).
    # When set on a video item, the template embeds this URL rather than
    # serving a local file. Ignored for photo items.
    # ------------------------------------------------------------------
    video_url = models.URLField(
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # caption
    # A short descriptive label shown beneath the media in the gallery
    # lightbox or slide view, e.g. "Boys marching at the annual parade".
    # Optional.
    # ------------------------------------------------------------------
    caption = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    # ------------------------------------------------------------------
    # order
    # Controls the display sequence of items within their album.
    # Lower numbers appear first. Allows the admin to pin the best
    # photo to the front without resorting to upload date.
    # ------------------------------------------------------------------
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Lower numbers appear first within the album.',
    )

    # ------------------------------------------------------------------
    # uploaded_at
    # Timestamp set when the item is first saved. Used as a fallback
    # sort key and for the "uploaded on" display in admin.
    # ------------------------------------------------------------------
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    @property
    def is_photo(self):
        """True when this item is a photo."""
        return self.media_type == self.MediaType.PHOTO

    @property
    def is_video(self):
        """True when this item is a video."""
        return self.media_type == self.MediaType.VIDEO

    def __str__(self):
        label = self.caption or f"Item {self.pk}"
        return f"{self.album.title} — {label} ({self.get_media_type_display()})"

    class Meta:
        verbose_name        = 'Gallery Item'
        verbose_name_plural = 'Gallery Items'
        ordering            = ['album', 'order', 'uploaded_at']
