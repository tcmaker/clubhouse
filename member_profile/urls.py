from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.index, name='index'),
    path('address/', views.address_form, name='address_form'),
    path('basic/', views.basic_info_form, name="basic_info_form"),
    path('email-confirm-notice/', views.email_confirm_notice, name="email_confirm_notice"),
    path('emergency_contact/', views.emergency_contact_form, name="emergency_contact_form"),
    path('phone/', views.phone_form, name='phone_form'),
]
