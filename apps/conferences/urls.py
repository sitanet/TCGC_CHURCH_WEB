"""
URL patterns for conferences.
"""
from django.urls import path
from . import views

app_name = "conferences"

urlpatterns = [
    path("", views.ConferenceListApiView.as_view(), name="conference_list"),
    path("<slug:slug>/", views.ConferenceDetailApiView.as_view(), name="conference_detail"),
]
