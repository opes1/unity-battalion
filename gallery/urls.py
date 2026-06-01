from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    path('gallery/',           views.gallery_list,  name='gallery_list'),
    path('gallery/<int:pk>/',  views.album_detail,  name='album_detail'),
]
