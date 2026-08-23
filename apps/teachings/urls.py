"""
URL patterns for teachings app.
"""
from django.urls import path
from . import views

app_name = "teachings"

urlpatterns = [
    path("sermons/", views.SermonListApiView.as_view(), name="sermon_list"),
    path("sermons/<slug:slug>/", views.SermonDetailApiView.as_view(), name="sermon_detail"),
    path("series/", views.SermonSeriesListApiView.as_view(), name="series_list"),
]
