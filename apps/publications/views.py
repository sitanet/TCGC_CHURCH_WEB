"""
Views and API for publications.
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Publication
from .serializers import PublicationSerializer


class PublicationListApiView(generics.ListAPIView):
    queryset = Publication.objects.filter(status="published")
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "is_featured"]
    search_fields = ["title", "author_name", "description"]


class PublicationDetailApiView(generics.RetrieveAPIView):
    queryset = Publication.objects.filter(status="published")
    serializer_class = PublicationSerializer
    lookup_field = "slug"
