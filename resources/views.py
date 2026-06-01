import os

from django.shortcuts import render

from .models import Resource


# -------------------------------------------------------------------------
# File-type icon map  →  (Font Awesome class, colour hex)
# -------------------------------------------------------------------------
_EXT_ICONS = {
    '.pdf':  ('fas fa-file-pdf',        '#e74c3c'),
    '.doc':  ('fas fa-file-word',       '#2b5797'),
    '.docx': ('fas fa-file-word',       '#2b5797'),
    '.xls':  ('fas fa-file-excel',      '#1d6f42'),
    '.xlsx': ('fas fa-file-excel',      '#1d6f42'),
    '.ppt':  ('fas fa-file-powerpoint', '#c0392b'),
    '.pptx': ('fas fa-file-powerpoint', '#c0392b'),
    '.zip':  ('fas fa-file-archive',    '#8e44ad'),
    '.rar':  ('fas fa-file-archive',    '#8e44ad'),
    '.mp4':  ('fas fa-file-video',      '#1a6b3a'),
    '.mp3':  ('fas fa-file-audio',      '#1a6b3a'),
    '.png':  ('fas fa-file-image',      '#d4a017'),
    '.jpg':  ('fas fa-file-image',      '#d4a017'),
    '.jpeg': ('fas fa-file-image',      '#d4a017'),
}
_DEFAULT_ICON = ('fas fa-file-alt', '#7a8098')


def _annotate(queryset):
    """
    Convert a Resource queryset to a list and attach two synthetic
    attributes to each item so templates don't need custom filters:

      file_icon        — Font Awesome class string
      file_icon_color  — hex colour string
      file_ext         — uppercase extension label, e.g. "PDF"
    """
    items = list(queryset)
    for r in items:
        if r.file and r.file.name:
            ext = os.path.splitext(r.file.name)[1].lower()
            r.file_icon, r.file_icon_color = _EXT_ICONS.get(ext, _DEFAULT_ICON)
            r.file_ext = ext.lstrip('.').upper()
        else:
            r.file_icon, r.file_icon_color = _DEFAULT_ICON
            r.file_ext = ''
    return items


def resources_list(request):
    """
    Public Resources page.

    Fetches all published resources and groups them into four sections
    (Officers, Parents, Boys, General).  Within each section resources
    are ordered newest-first (the model's default ordering).

    Each resource is annotated with file_icon / file_icon_color / file_ext
    so the template can show the correct Font Awesome icon and badge.

    Audience visibility:
      • All resources with is_published=True are shown to every visitor.
      • Resources with audience='officers' display a lock badge to signal
        that the content is intended for officers only.
    """
    base_qs = Resource.objects.filter(is_published=True).order_by('-uploaded_at')

    categories = [
        {
            'key':         Resource.Category.OFFICERS,
            'label':       'Officers',
            'icon':        'fas fa-user-tie',
            'accent':      'var(--bb-blue)',
            'accent_bg':   'var(--bb-blue-dark)',
            'description': (
                'Training manuals, administrative forms, meeting guides, '
                'and reference documents for BB officers.'
            ),
            'resources':   _annotate(base_qs.filter(category=Resource.Category.OFFICERS)),
        },
        {
            'key':         Resource.Category.PARENTS,
            'label':       'Parents',
            'icon':        'fas fa-users',
            'accent':      'var(--bb-red)',
            'accent_bg':   'var(--bb-red-dark)',
            'description': (
                'Parent guides, permission forms, programme overviews, '
                'and answers to frequently asked questions.'
            ),
            'resources':   _annotate(base_qs.filter(category=Resource.Category.PARENTS)),
        },
        {
            'key':         Resource.Category.BOYS,
            'label':       'Boys',
            'icon':        'fas fa-child',
            'accent':      '#1a6b3a',
            'accent_bg':   '#144f2c',
            'description': (
                'Activity sheets, badge requirement checklists, scripture memory cards, '
                'and programme materials for boys.'
            ),
            'resources':   _annotate(base_qs.filter(category=Resource.Category.BOYS)),
        },
        {
            'key':         Resource.Category.GENERAL,
            'label':       'General',
            'icon':        'fas fa-file-alt',
            'accent':      'var(--bb-gold)',
            'accent_bg':   '#8a6910',
            'description': (
                'Council notices, newsletters, annual reports, policies, '
                'and general documents available to everyone.'
            ),
            'resources':   _annotate(base_qs.filter(category=Resource.Category.GENERAL)),
        },
    ]

    context = {
        'page_title': 'Resources',
        'categories': categories,
    }
    return render(request, 'resources/resources_list.html', context)
