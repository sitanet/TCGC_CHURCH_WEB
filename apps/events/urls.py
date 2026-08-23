"""
URL patterns for events.
"""
from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.EventListApiView.as_view(), name="event_list"),
    path("<slug:slug>/", views.EventDetailApiView.as_view(), name="event_detail"),
    path("<slug:slug>/register/", views.EventRegisterApiView.as_view(), name="event_register"),
]
