from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.index, name='index'),
    path('card/', views.card_form, name='card_form'),
    path('subscription/', views.subscription_form, name='subscription_form'),

    # Administered Households
    path('households/', views.household_list, name='household_list'),
    path('households/<uuid>/', views.household_detail, name='household_detail'),
    path('households/<uuid>/edit/', views.household_form, name='household_form'),

    # Enrollment
    path('enroll/', views.enroll_autopay_form, name='enroll_payment_option_form'),
    path('enroll/invoice/', views.enroll_invoice_form, name='enroll_invoice_form'),
]
