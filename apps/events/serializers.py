"""
Serializers for events.
"""
from rest_framework import serializers
from .models import Event, EventCategory, EventRegistration


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ["id", "name", "slug"]


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    registrations_count = serializers.IntegerField(source="registrations.count", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "category_name",
            "tagline",
            "description",
            "banner_image",
            "start_datetime",
            "end_datetime",
            "is_recurring",
            "recurrence_rule",
            "venue_name",
            "venue_address",
            "is_online",
            "stream_link",
            "requires_registration",
            "max_attendees",
            "is_free",
            "registrations_count",
            "is_featured",
        ]


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ["id", "event", "full_name", "email", "phone", "notes", "created_at"]
