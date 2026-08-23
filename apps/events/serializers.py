"""
Serializers for events and registrations.
"""
from rest_framework import serializers
from .models import Event, EventCategory, EventRegistration


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "slug"]


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    speaker_display = serializers.CharField(source="get_speaker_display", read_only=True)
    ministry_name = serializers.CharField(source="ministry.name", read_only=True)
    registrations_count = serializers.IntegerField(source="registrations.count", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "category_name",
            "ministry",
            "ministry_name",
            "speaker",
            "speaker_name",
            "speaker_display",
            "tagline",
            "description",
            "banner_image",
            "start_datetime",
            "end_datetime",
            "is_recurring",
            "recurrence_rule",
            "venue_name",
            "venue_address",
            "location",
            "is_online",
            "stream_link",
            "requires_registration",
            "registration_url",
            "max_attendees",
            "is_free",
            "contact_email",
            "contact_phone",
            "status",
            "is_featured",
            "registrations_count",
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ["id", "event", "full_name", "email", "phone", "notes", "is_confirmed", "created_at"]
