"""
Views and API for people.
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Person, LeadershipCategory
from .serializers import PersonSerializer, LeadershipCategorySerializer


class PersonListApiView(generics.ListAPIView):
    queryset = Person.objects.filter(status="published")
    serializer_class = PersonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_featured"]
    search_fields = ["name", "title", "biography"]
    ordering_fields = ["sort_order", "name"]


class PersonDetailApiView(generics.RetrieveAPIView):
    queryset = Person.objects.filter(status="published")
    serializer_class = PersonSerializer
    lookup_field = "slug"
