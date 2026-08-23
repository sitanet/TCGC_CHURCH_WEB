"""
URL patterns for publications.
"""
from django.urls import path
from . import views

app_name = "publications"

urlpatterns = [
    path("", views.PublicationListApiView.as_view(), name="publication_list"),
    path("<slug:slug>/", views.PublicationDetailApiView.as_view(), name="publication_detail"),
]
