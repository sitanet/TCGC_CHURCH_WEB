"""
Serializers for ministries, recurring meetings, and campus locations.
"""
from rest_framework import serializers
from .models import Ministry, ChurchMeeting, ChurchLocation


class ChurchLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchLocation
        fields = [
            "id",
            "name",
            "slug",
            "address",
            "city",
            "state",
            "country",
            "is_main_campus",
            "phone",
            "email",
            "google_maps_url",
            "photo",
            "sort_order",
        ]


class ChurchMeetingSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)
    ministry_name = serializers.CharField(source="ministry.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = ChurchMeeting
        fields = [
            "id",
            "name",
            "slug",
            "ministry",
            "ministry_name",
            "location",
            "location_name",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "location_hall",
            "is_online",
            "stream_link",
            "description",
            "is_active",
            "sort_order",
        ]


class MinistrySerializer(serializers.ModelSerializer):
    leader_name = serializers.CharField(source="leader.name", read_only=True)
    meetings = ChurchMeetingSerializer(many=True, read_only=True)

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
            "contact_phone",
            "accepts_volunteers",
            "sort_order",
            "is_featured",
            "meetings",
        ]
