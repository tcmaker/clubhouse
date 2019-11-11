from django.contrib import admin
from . import models
# Register your models here.

# admin.site.register(models.Membership)
admin.site.register(models.Discount)
admin.site.register(models.PaymentPlan)

@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'family_name', 'given_name', 'email', 'phone_number')
    fieldsets = (
        ('Basic Information', {
            'fields': ('given_name', 'family_name', 'email', 'member_since', 'membership', 'account')
        }),

        ('Address', {
            'fields': ('address_street1', 'address_street2', 'address_city', 'address_state', 'address_zip')
        }),

        ('Phone', {
            'fields': ('phone_number', 'phone_can_receive_sms')
        }),

        ('Emergency Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
    )

@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'membership_type', 'status', 'membership_contact')
