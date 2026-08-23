"""
URL patterns for media_library.
"""
from django.urls import path
from . import views

app_name = "media_library"

urlpatterns = [
    path("galleries/", views.PhotoGalleryListApiView.as_view(), name="gallery_list"),
    path("galleries/<slug:slug>/", views.PhotoGalleryDetailApiView.as_view(), name="gallery_detail"),
    path("assets/", views.MediaAssetListApiView.as_view(), name="asset_list"),
]
