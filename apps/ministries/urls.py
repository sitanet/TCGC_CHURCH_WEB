"""
URL patterns for ministries.
"""
from django.urls import path
from . import views

app_name = "ministries"

urlpatterns = [
    path("", views.MinistryListApiView.as_view(), name="ministry_list"),
    path("<slug:slug>/", views.MinistryDetailApiView.as_view(), name="ministry_detail"),
]
