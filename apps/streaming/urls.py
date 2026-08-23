"""
URL patterns for streaming.
"""
from django.urls import path
from . import views

app_name = "streaming"

urlpatterns = [
    path("status/", views.LiveStreamStatusApiView.as_view(), name="status"),
]
