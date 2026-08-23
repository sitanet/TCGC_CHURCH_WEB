"""
Serializers for ministries.
"""
from rest_framework import serializers
from .models import Ministry


class MinistrySerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.name", read_only=True)

    class Meta:
        model = Ministry
        fields = [
            "id",
            "name",
            "slug",
            "tagline",
            "description",
            "icon_name",
            "cover_image",
            "leader",
            "leader_name",
            "meeting_schedule",
            "meeting_location",
            "contact_email",
            "accepts_volunteers",
            "sort_order",
            "is_featured",
        ]
