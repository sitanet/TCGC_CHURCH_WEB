"""
Serializers for announcements.
"""
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "message",
            "link_url",
            "link_label",
            "priority",
            "show_banner",
            "is_active",
            "expires_at",
            "created_at",
        ]
