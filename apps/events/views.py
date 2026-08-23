"""
Views and API for events.
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer


class EventListApiView(generics.ListAPIView):
    queryset = Event.objects.filter(status="published")
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_featured", "is_online"]
    search_fields = ["title", "tagline", "description", "venue_name"]
    ordering_fields = ["start_datetime", "created_at"]


class EventDetailApiView(generics.RetrieveAPIView):
    queryset = Event.objects.filter(status="published")
    serializer_class = EventSerializer
    lookup_field = "slug"


class EventRegisterApiView(generics.CreateAPIView):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
