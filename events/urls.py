from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('events/',              views.events_list,     name='events_list'),
    path('events/<int:pk>/',     views.event_detail,    name='event_detail'),
]
