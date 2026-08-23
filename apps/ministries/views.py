"""
Views and API for ministries.
"""
from rest_framework import generics, filters
from .models import Ministry
from .serializers import MinistrySerializer


class MinistryListApiView(generics.ListAPIView):
    queryset = Ministry.objects.filter(status="published")
    serializer_class = MinistrySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "tagline", "description"]


class MinistryDetailApiView(generics.RetrieveAPIView):
    queryset = Ministry.objects.filter(status="published")
    serializer_class = MinistrySerializer
    lookup_field = "slug"
