"""
URL patterns for search app.
"""
from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path("query/", views.UnifiedSearchApiView.as_view(), name="unified_search"),
]
