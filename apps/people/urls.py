"""
URL patterns for people.
"""
from django.urls import path
from . import views

app_name = "people"

urlpatterns = [
    path("", views.PersonListApiView.as_view(), name="people_list"),
    path("<slug:slug>/", views.PersonDetailApiView.as_view(), name="people_detail"),
]
