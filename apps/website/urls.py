"""
URL configuration for public website.
"""
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("visit/", views.VisitView.as_view(), name="visit"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
