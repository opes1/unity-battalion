from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Logout
    path('accounts/logout/', views.logout_view,   name='logout'),

    # Hidden super-admin portal — URL is deliberately non-obvious
    path('battalion-control/', views.super_login, name='super_login'),
]
