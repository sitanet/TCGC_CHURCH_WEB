"""
Views and API for announcements.
"""
from rest_framework import generics
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementListApiView(generics.ListAPIView):
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
