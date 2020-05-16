from django.urls import path
from . import views

app_name = 'renew'

urlpatterns = [
    path('', views.index, name='index'),
]
