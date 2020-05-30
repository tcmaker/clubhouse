from django.contrib import admin
from .models import User
from . import views
from django.urls import path
from django import forms
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
import json

# class AccountsAdminSite(AdminSite):

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name', 'first_name', 'email')

    search_fields = ['last_name', 'first_name', 'email', 'username']

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
            'fields': ('civicrm_identifier', 'civicrm_keyfob_code'),
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
        ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('civicrm-import/', views.import_civicrm_contact, name="accounts_user_civicrm_import"),
            path('civicrm-import/preview/', views.import_civicrm_contact_preview, name="accounts_user_civicrm_import_preview")
        ]
        return my_urls + urls
