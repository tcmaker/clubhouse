from django.contrib import admin
from .models import Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('family_name', 'given_name', 'email', 'application_completed_at', 'keyfob_issued_at', 'account_invitation_created_at', 'account_invitation_accepted_at')

    search_fields = ['family_name', 'given_name', 'email', 'civicrm_identifier', 'stripe_identifier']

    ordering = ['family_name', 'given_name']
