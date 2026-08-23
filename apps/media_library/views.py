"""
Views and API for media_library.
"""
from rest_framework import generics, filters
from .models import PhotoGallery, MediaAsset
from .serializers import PhotoGallerySerializer, MediaAssetSerializer


class PhotoGalleryListApiView(generics.ListAPIView):
    queryset = PhotoGallery.objects.filter(status="published")
    serializer_class = PhotoGallerySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]


class PhotoGalleryDetailApiView(generics.RetrieveAPIView):
    queryset = PhotoGallery.objects.filter(status="published")
    serializer_class = PhotoGallerySerializer
    lookup_field = "slug"


class MediaAssetListApiView(generics.ListAPIView):
    queryset = MediaAsset.objects.filter(status="published")
    serializer_class = MediaAssetSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "tags"]
