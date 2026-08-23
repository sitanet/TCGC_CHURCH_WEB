"""
API Views and public views for Teachings.
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sermon, SermonSeries
from .serializers import SermonSerializer, SermonSeriesSerializer


class SermonListApiView(generics.ListAPIView):
    """
    API endpoint listing published sermons.
    """
    queryset = Sermon.objects.filter(status="published")
    serializer_class = SermonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["series", "speaker_name", "is_featured"]
    search_fields = ["title", "speaker_name", "scripture_reference", "summary"]
    ordering_fields = ["preached_date", "created_at", "play_count"]


class SermonDetailApiView(generics.RetrieveAPIView):
    """
    API endpoint retrieving a single sermon by slug.
    """
    queryset = Sermon.objects.filter(status="published")
    serializer_class = SermonSerializer
    lookup_field = "slug"


class SermonSeriesListApiView(generics.ListAPIView):
    """
    API endpoint listing published sermon series.
    """
    queryset = SermonSeries.objects.filter(status="published")
    serializer_class = SermonSeriesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]
