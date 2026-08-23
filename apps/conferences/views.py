"""
Views and API for conferences.
"""
from rest_framework import generics, filters
from .models import Conference
from .serializers import ConferenceSerializer


class ConferenceListApiView(generics.ListAPIView):
    queryset = Conference.objects.filter(status="published")
    serializer_class = ConferenceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "theme", "description"]


class ConferenceDetailApiView(generics.RetrieveAPIView):
    queryset = Conference.objects.filter(status="published")
    serializer_class = ConferenceSerializer
    lookup_field = "slug"
