from django.urls import path
from . import views

app_name = 'timeslots'

urlpatterns = [

    # Managing reservations
    path('reservations/', views.reservation_list, name="reservation_list"),
    path('reservations/<reservation_id>/', views.reservation_detail, name="reservation_detail"),
    path('reservations/<reservation_id>/cancel/', views.reservation_cancel, name="reservation_cancel"),

    # Reserving timeslots
    path('', views.area_list, name='index'),
    path('<area_id>/', views.area_calendar, name='area_calendar'),
    path('<area_id>/close', views.area_close_block_of_timeslots, name='area_close_block_of_timeslots'),
    path('<area_id>/events', views.events_as_json, name='events_as_json'),
    path('<area_id>/<slug>/', views.timeslot_detail, name="timeslot_detail"),
    path('<area_id>/<slug>/status', views.close_timeslot, name="timeslot_close"),
    path('<area_id>/<slug>/reserve', views.reservation_form, name="reservation_form"),

    # path('reservations/', views.reservation_form, name="reservation_delete"),

    # path('', signup.index, name='index'),
    # path('account', signup.AccountView.as_view(), name=steps.ACCOUNT_INFO_STEP),
    # path('contact', signup.ContactView.as_view(), name=steps.CONTACT_INFO_STEP),
    # path('dues', signup.DuesView.as_view(), name=steps.DUES_INFO_STEP),
    # path('legal', signup.LiabilityWaiverView.as_view(), name=steps.LEGAL_STEP),
    # # path('household', signup.InvitationView.as_view(), name=steps.INVITE_STEP),
    # path('final', signup.final, name=steps.DONE_STEP),
]
