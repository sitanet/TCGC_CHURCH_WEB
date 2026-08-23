"""
URL patterns for analytics.
"""
from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("record/play/", views.RecordMediaPlayApiView.as_view(), name="record_play"),
    path("record/download/", views.RecordDownloadApiView.as_view(), name="record_download"),
]
