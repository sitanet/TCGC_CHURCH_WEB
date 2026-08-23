"""
Serializers for streaming.
"""
from rest_framework import serializers
from .models import LiveStreamChannel


class LiveStreamChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStreamChannel
        fields = [
            "id",
            "title",
            "platform",
            "stream_url",
            "is_live",
            "current_topic",
            "current_speaker",
            "next_broadcast_time",
            "offline_poster_image",
            "viewer_count",
        ]
