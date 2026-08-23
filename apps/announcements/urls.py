"""
URL patterns for announcements.
"""
from django.urls import path
from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.AnnouncementListApiView.as_view(), name="announcement_list"),
]
