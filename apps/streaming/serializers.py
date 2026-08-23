"""
Serializers for streaming.
"""
from rest_framework import serializers
from .models import LiveStreamChannel


class LiveStreamChannelSerializer(serializers.ModelSerializer):
    stream_status_display = serializers.CharField(source="get_stream_status_display", read_only=True)

    class Meta:
        model = LiveStreamChannel
        fields = [
            "id",
            "title",
            "platform",
            "stream_status",
            "stream_status_display",
            "stream_url",
            "audio_stream_url",
            "is_live",
            "current_program",
            "current_topic",
            "current_speaker",
            "start_time",
            "end_time",
            "next_program",
            "next_broadcast_time",
            "offline_poster_image",
            "viewer_count",
        ]
