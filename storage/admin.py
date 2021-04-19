from django.contrib import admin
from .models import Cubby, CubbyRequest

@admin.register(Cubby)
class CubbyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'aisle', 'assignee')
    autocomplete_fields = ['assignee']
    search_fields = ['assignee__first_name', 'assignee__last_name', 'assignee__email', 'assignee__username']

    list_filter = ['aisle', 'assignee__civicrm_membership_status']

    def get_ordering(self, request):
        return ['identifier']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.extra(
            select={'identifier': 'CAST(identifier AS INTEGER)'}
        ).order_by('identifier')

@admin.register(CubbyRequest)
class CubbyRequest(admin.ModelAdmin):
    date_hierarchy = 'requested_at'
    list_display = ('requested_at', 'member_last_name', 'member_first_name', 'member_membership_status')
    search_fields = ['member__first_name', 'member__last_name']
    autocomplete_fields = ['member']
    list_filter = ['member__civicrm_membership_status']

    def member_last_name(self, obj):
        return obj.member.last_name

    def member_first_name(self, obj):
        return obj.member.first_name

    def member_membership_status(self, obj):
        return obj.member.civicrm_membership_status

    def get_ordering(self, request):
        return ['requested_at']
