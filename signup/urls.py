from django.urls import path
from .views import approval, signup, invite, steps

app_name = 'signup'

urlpatterns = [
    # New Signups
    path('', signup.index, name='index'),
    path('account', signup.AccountView.as_view(), name=steps.ACCOUNT_INFO_STEP),
    path('contact', signup.ContactView.as_view(), name=steps.CONTACT_INFO_STEP),
    path('dues', signup.DuesView.as_view(), name=steps.DUES_INFO_STEP),
    path('dues/card', signup.CardView.as_view(), name=steps.PAYMENT_CARD_STEP),
    path('dues/paypal', signup.BraintreeView.as_view(), name=steps.PAYMENT_PAYPAL_STEP),
    path('legal', signup.LiabilityWaiverView.as_view(), name=steps.LEGAL_STEP),
    path('household', signup.InvitationView.as_view(), name=steps.INVITE_STEP),
    path('final', signup.final, name=steps.DONE_STEP),

    # Invitation to join existing membership
    path('invite/accept/<code>', invite.accept_invite, name='invite_accept'),
    path('invite/account', invite.InviteAccountView.as_view(), name=steps.INVITE_ACCOUNT_INFO_STEP),
    path('invite/contact', invite.InviteContactView.as_view(), name=steps.INVITE_CONTACT_INFO_STEP),
    path('invite/legal', invite.InviteLegalView.as_view(), name=steps.INVITE_LEGAL_STEP),
    path('invite/final', invite.invite_final, name=steps.INVITE_FINAL_STEP),

    # Approvals
    path('pending/', approval.index, name="approval_index"),
    # path('pending/households/', approval.PendingSignupList.as_view(), name="approval_membership_list"),
    path('pending/households/<int:pk>', approval.PendingSignupDetail.as_view(), name="approval_membership_detail"),
    path('pending/households/<int:pk>/approve', approval.ApproveHouseholdForm.as_view(), name="approval_membership_form"),
    path('pending/households/<int:pk>/reject', approval.RejectHouseholdForm.as_view(), name="approval_membership_rejection_form"),

    # path('pending/invites/', approval.PendingInvitationList.as_view(), name="approval_invite_list"),
    path('pending/invites/<int:pk>', approval.PendingInvitationDetail.as_view(), name="approval_invite_detail"),
    path('pending/invites/<int:pk>/approve', approval.PendingInvitationForm.as_view(), name="approval_invite_form"),
    path('pending/invites/<int:pk>/reject', approval.PendingInvitationForm.as_view(), name="approval_invite_rejection_form"),
]
