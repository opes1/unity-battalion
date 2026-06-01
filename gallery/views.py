from django.shortcuts import render, get_object_or_404

from .models import Album, GalleryItem
from companies.models import Company


def gallery_list(request):
    """
    Public gallery index — shows all albums as a card grid.

    Supports optional GET filters:
      • company=<pk>   — show only albums for that company
      • year=<yyyy>    — show only albums created in that year

    Sidebar lists all companies that have at least one album, and a
    distinct list of years to let visitors drill down.
    """
    albums = Album.objects.select_related('company', 'event').prefetch_related('items')

    # ---- Filters -------------------------------------------------------
    company_pk = request.GET.get('company')
    year       = request.GET.get('year')

    if company_pk:
        albums = albums.filter(company__pk=company_pk)
    if year:
        albums = albums.filter(created_at__year=year)

    albums = albums.order_by('-created_at')

    # ---- Sidebar data --------------------------------------------------
    companies_with_albums = (
        Company.objects
        .filter(albums__isnull=False)
        .distinct()
        .order_by('name')
    )

    years = (
        Album.objects
        .dates('created_at', 'year', order='DESC')
    )

    context = {
        'page_title':            'Gallery',
        'albums':                albums,
        'companies_with_albums': companies_with_albums,
        'years':                 years,
        'selected_company':      company_pk,
        'selected_year':         year,
    }
    return render(request, 'gallery/gallery_list.html', context)


def album_detail(request, pk):
    """
    Shows all media inside a single album.

    Separates items into:
      • photos  — for the lightbox grid
      • videos  — for the video section beneath the grid
    """
    album  = get_object_or_404(Album.objects.select_related('company', 'event'), pk=pk)
    photos = album.items.filter(media_type=GalleryItem.MediaType.PHOTO).order_by('order', 'uploaded_at')
    videos = album.items.filter(media_type=GalleryItem.MediaType.VIDEO).order_by('order', 'uploaded_at')

    # Sidebar: other albums from the same company (or battalion-wide)
    if album.company:
        related_albums = (
            Album.objects
            .filter(company=album.company)
            .exclude(pk=album.pk)
            .order_by('-created_at')[:4]
        )
    else:
        related_albums = (
            Album.objects
            .filter(company__isnull=True)
            .exclude(pk=album.pk)
            .order_by('-created_at')[:4]
        )

    context = {
        'page_title':     album.title,
        'album':          album,
        'photos':         photos,
        'videos':         videos,
        'related_albums': related_albums,
    }
    return render(request, 'gallery/album_detail.html', context)
