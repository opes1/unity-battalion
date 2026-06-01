from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Public-facing staff login — company admins use this
    path('accounts/login/',  views.company_login, name='login'),

    # Logout — works for both roles
    path('accounts/logout/', views.logout_view,   name='logout'),

    # Hidden super-admin portal — URL is deliberately non-obvious
    path('battalion-control/', views.super_login, name='super_login'),
]
