from django.contrib import admin
from .models import Cubby, CubbyRequest

@admin.register(Cubby)
class CubbyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'aisle', 'assignee')
    autocomplete_fields = ['assignee']
    search_fields = ['assignee__first_name', 'assignee__last_name', 'assignee__email', 'assignee__username']

    list_filter = ['aisle', 'assignee__civicrm_membership_status']

    def get_ordering(self, request):
        return ['int_identifier']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.extra(
            select={'int_identifier': 'CAST(identifier AS INTEGER)'}
        ).order_by('int_identifier')


admin.site.register(CubbyRequest)
