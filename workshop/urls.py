from django.urls import path
from . import views

app_name = 'workshop'
urlpatterns = [
    path('', views.index, name='index'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/<department_id>/', views.department_detail, name='department_detail'),
    path('departments/<department_id>/donate/', views.department_donate, name='department_donate'),
    path('departments/<department_id>/donate/generate_stripe_session/', views.department_checkout, name='department_checkout'),
    path('departments/<department_id>/donate/callback/', views.department_checkout_callback, name='department_checkout_callback'),
]
