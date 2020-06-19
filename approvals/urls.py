from django.urls import path
from . import views

app_name = 'approvals'
urlpatterns = [
    # New Signups
    path('', views.IndexView.as_view(), name="index"),

    #### Registrations ####
    path('registrations/', views.RegistrationIndexView.as_view(), name="registration_index"),

    # First, we issue Keyfobs
    path('registrations/pending-keyfobs/', views.RegistrationPendingKeyfobList.as_view(), name="registration_pending_keyfob_list"),
    path('registrations/pending-keyfobs/<int:pk>/', views.RegistrationPendingKeyfobDetail.as_view(), name="registration_pending_keyfob_detail"),
    path('registrations/pending-keyfobs/<int:pk>/form/', views.RegistrationPendingKeyfobForm.as_view(), name="registration_pending_keyfob_form"),

    # After orientation, registrations need final approval.
    path('registrations/pending-invites/', views.RegistrationPendingInviteList.as_view(), name="registration_pending_invite_list"),
    path('registrations/pending-invites/<int:pk>/', views.RegistrationPendingInviteDetail.as_view(), name="registration_pending_invite_detail"),
    path('registrations/pending-invites/<int:pk>/form/', views.RegistrationPendingInviteForm.as_view(), name="registration_pending_invite_form"),

    #### Renewals ####

    # TODO: Implementation

    #### Family Member Invitations ####

    # TODO: Implementation
]
