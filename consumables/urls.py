from django.urls import path
from . import views

app_name = 'consumables'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('callback/', views.callback, name='callback'),
    path('products/<product_id>/', views.product_detail, name='product_detail'),
    path('products/<product_id>/generate_stripe_session/', views.generate_stripe_session, name='checkout'),
]
