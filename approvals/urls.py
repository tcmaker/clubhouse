from django.urls import path
from . import views

app_name = 'approvals'
urlpatterns = [
    # New Signups
    path('', views.index, name="approval_index"),
    # path('pending/households/', views.PendingSignupList.as_view(), name="approval_membership_list"),
    path('pending/households/<int:pk>', views.PendingSignupDetail.as_view(), name="approval_membership_detail"),
    path('pending/households/<int:pk>/approve', views.ApproveHouseholdForm.as_view(), name="approval_membership_form"),
    path('pending/households/<int:pk>/reject', views.RejectHouseholdForm.as_view(), name="approval_membership_rejection_form"),
    #
    # # path('pending/invites/', approval.PendingInvitationList.as_view(), name="approval_invite_list"),
    # path('pending/invites/<int:pk>', approval.PendingInvitationDetail.as_view(), name="approval_invite_detail"),
    # path('pending/invites/<int:pk>/approve', approval.PendingInvitationForm.as_view(), name="approval_invite_form"),
    # path('pending/invites/<int:pk>/reject', approval.PendingInvitationForm.as_view(), name="approval_invite_rejection_form"),
]
