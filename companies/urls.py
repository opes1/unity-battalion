from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('companies/',           views.companies_list,  name='companies_list'),
    path('companies/map/',       views.companies_map,   name='companies_map'),
    path('companies/<int:pk>/',  views.company_detail,  name='company_detail'),
]
