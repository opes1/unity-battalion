from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    # ---- Super-admin overview ----------------------------------------
    path('super-dashboard/',
         views.super_dashboard,
         name='super_dashboard'),

    # ---- Companies ---------------------------------------------------
    path('super-dashboard/companies/',
         views.manage_companies,
         name='manage_companies'),

    path('super-dashboard/companies/<int:pk>/edit/',
         views.edit_company,
         name='edit_company'),

    path('super-dashboard/companies/<int:pk>/toggle/',
         views.toggle_company,
         name='toggle_company'),

    # ---- Approval requests ------------------------------------------
    path('super-dashboard/approvals/',
         views.pending_approvals,
         name='pending_approvals'),

    path('super-dashboard/approvals/<int:pk>/approve/',
         views.approve_request,
         name='approve_request'),

    path('super-dashboard/approvals/<int:pk>/reject/',
         views.reject_request,
         name='reject_request'),

    # ---- User management --------------------------------------------
    path('super-dashboard/users/',
         views.manage_users,
         name='manage_users'),

    path('super-dashboard/users/<int:pk>/approve/',
         views.approve_user,
         name='approve_user'),

    # ---- Events -----------------------------------------------------
    path('super-dashboard/events/',
         views.manage_events,
         name='manage_events'),

    path('super-dashboard/events/add/',
         views.add_event,
         name='add_event'),

    path('super-dashboard/events/<int:pk>/edit/',
         views.edit_event,
         name='edit_event'),

    path('super-dashboard/events/<int:pk>/delete/',
         views.delete_event,
         name='delete_event'),

    # ---- Gallery ----------------------------------------------------
    path('super-dashboard/gallery/',
         views.manage_gallery,
         name='manage_gallery'),

    path('super-dashboard/gallery/add/',
         views.add_album,
         name='add_album'),

    path('super-dashboard/gallery/<int:pk>/add-photos/',
         views.add_photos_to_album,
         name='add_photos_to_album'),

    path('super-dashboard/gallery/<int:pk>/delete/',
         views.delete_album,
         name='delete_album'),

    # ---- Resources --------------------------------------------------
    path('super-dashboard/resources/',
         views.manage_resources,
         name='manage_resources'),

    path('super-dashboard/resources/add/',
         views.add_resource,
         name='add_resource'),

    path('super-dashboard/resources/<int:pk>/delete/',
         views.delete_resource,
         name='delete_resource'),

    path('super-dashboard/resources/<int:pk>/toggle/',
         views.toggle_resource,
         name='toggle_resource'),

    # ---- Contact messages -------------------------------------------
    path('super-dashboard/messages/',
         views.view_messages,
         name='view_messages'),

    # ---- Content management -----------------------------------------
    path('super-dashboard/about/',
         views.edit_about,
         name='edit_about'),

    path('super-dashboard/contact-info/',
         views.edit_contact_info,
         name='edit_contact_info'),

    # ---- Core Values ------------------------------------------------
    path('super-dashboard/core-values/',
         views.manage_core_values,
         name='manage_core_values'),

    path('super-dashboard/core-values/add/',
         views.add_core_value,
         name='add_core_value'),

    path('super-dashboard/core-values/<int:pk>/edit/',
         views.edit_core_value,
         name='edit_core_value'),

    path('super-dashboard/core-values/<int:pk>/delete/',
         views.delete_core_value,
         name='delete_core_value'),

    # ---- Leadership Profiles ----------------------------------------
    path('super-dashboard/leadership/',
         views.manage_leadership,
         name='manage_leadership'),

    path('super-dashboard/leadership/add/',
         views.add_leader,
         name='add_leader'),

    path('super-dashboard/leadership/<int:pk>/edit/',
         views.edit_leader,
         name='edit_leader'),

    path('super-dashboard/leadership/<int:pk>/delete/',
         views.delete_leader,
         name='delete_leader'),

    path('super-dashboard/leadership/<int:pk>/toggle/',
         views.toggle_leader,
         name='toggle_leader'),

    # ================================================================
    # Company-Admin Dashboard
    # ================================================================

    path('company-dashboard/',
         views.company_dashboard,
         name='company_dashboard'),

    path('company-dashboard/edit-info/',
         views.edit_company_info,
         name='edit_company_info'),

    path('company-dashboard/officers/',
         views.manage_officers,
         name='manage_officers'),

    path('company-dashboard/members/',
         views.manage_members,
         name='manage_members'),

    path('company-dashboard/requests/',
         views.my_requests,
         name='my_requests'),
]
