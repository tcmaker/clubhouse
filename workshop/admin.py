from django.contrib import admin
from .models import Area, Department

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_manager', 'shop_contact_email')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_manager', 'shop_contact_email')
