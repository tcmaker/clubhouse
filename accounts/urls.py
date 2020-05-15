from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('signout', views.OIDCLogoutView.as_view(), name='signout'),
    path('login/', views.login, name="login"),
    path('password/', views.change_password, name="change_password"),
]
