"""
Serializers for conferences.
"""
from rest_framework import serializers
from .models import Conference, ConferenceSpeaker, ConferenceSession


class ConferenceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSession
        fields = ["id", "session_title", "speaker_info", "session_date", "start_time", "end_time", "location_hall", "description"]


class ConferenceSpeakerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = ConferenceSpeaker
        fields = ["id", "display_name", "title_override", "photo_override", "sort_order"]


class ConferenceSerializer(serializers.ModelSerializer):
    sessions = ConferenceSessionSerializer(many=True, read_only=True)
    speakers = ConferenceSpeakerSerializer(many=True, read_only=True)

    class Meta:
        model = Conference
        fields = [
            "id",
            "title",
            "slug",
            "theme",
            "description",
            "banner_image",
            "start_date",
            "end_date",
            "venue",
            "registration_link",
            "schedule_document",
            "sessions",
            "speakers",
            "is_featured",
        ]
