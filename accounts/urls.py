from django.urls import path
from . import views
from .views import onboarding

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('signout', views.OIDCLogoutView.as_view(), name='signout'),
    path('login/', views.login, name="login"),
    path('password/', views.change_password, name="change_password"),

    # Onboarding
    path('onboard/', views.onboarding.accept, name="accept_invite"),
    path('onboard/password/', views.onboarding.set_password, name="set_password"),
    path('onboard/instructions/', views.onboarding.instructions, name="instructions"),
]
