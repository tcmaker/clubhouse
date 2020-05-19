from django.contrib import admin
from .models import User

# class AccountsAdminSite(AdminSite):

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'last_name', 'first_name', 'email', 'username')
    fieldsets = (
        ('Basic Information', {
            'fields': ('last_name', 'first_name', 'email'),
        }),

        ('Account Information', {
            'fields': ('username', 'sub'),
        }),

        ('Integrations', {
            'fields': ('civicrm_identifier', 'member_identifier')
        }),

        ('Advanced', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        })
    )
