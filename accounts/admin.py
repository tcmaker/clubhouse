from django.contrib import admin
from .models import User, Invitation
from . import views
from django.urls import path

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('user_family_name', 'user_given_name',  'user_email', 'created_at', 'expires_at', 'accepted_at')

    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'uuid']

    def user_family_name(self, obj):
        return obj.user.last_name

    def user_given_name(self, obj):
        return obj.user.first_name

    def user_email(self, obj):
        return obj.user.email



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name', 'first_name', 'email', 'civicrm_membership_status')

    search_fields = ['last_name', 'first_name', 'email', 'username']

    list_filter = ['civicrm_membership_status']

    ordering = ['last_name', 'first_name']

    filter_horizontal = ('user_permissions', 'groups',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('last_name', 'first_name', 'email'),
        }),

        ('Account Information', {
            'fields': ('username', 'sub'),
        }),

        ('Integrations', {
            'fields': ('membership_person_record', 'civicrm_identifier', 'civicrm_keyfob_code', 'civicrm_membership_status'),
        }),

        ('Advanced', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        })
    )

    # def has_add_permission(self, request):
    #     return False

    def get_readonly_fields(self, request, obj=None):
        return [
            'first_name',
            'last_name',
            'email',
            'username',
            'sub',
            'civicrm_identifier',
            'civicrm_keyfob_code',
            'civirm_membership_status',
        ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('civicrm-import/', views.import_civicrm_contact, name="accounts_user_civicrm_import"),
            path('civicrm-import/preview/', views.import_civicrm_contact_preview, name="accounts_user_civicrm_import_preview"),
            path('<int:pk>/cognito/', views.cognito_admin, name="accounts_user_cognito_admin"),
        ]
        return my_urls + urls
