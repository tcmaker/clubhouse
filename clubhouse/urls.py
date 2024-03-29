"""clubhouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = "Clubhouse Admin"
admin.site.site_title = "Clubhouse Admin"
admin.site.index_title = "Clubhouse Admin"

urlpatterns = [
    path('oidc/', include('mozilla_django_oidc.urls')),

    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('approvals/', include('approvals.urls')),
    path('billing/', include('billing.urls')),
    path('consumables/', include('consumables.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('profile/', include('member_profile.urls')),
    path('renew/', include('renew.urls')),
    path('signup/', include('signup.urls')),
    path('timeslots/', include('timeslots.urls')),
    path('workshop/', include('workshop.urls')),

    # Documentation for the project
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # Generally, this should go last.
    path('admin/', admin.site.urls),
]
