"""
Serializers for teachings application.
"""
from rest_framework import serializers
from .models import Sermon, SermonSeries


class SermonSeriesSerializer(serializers.ModelSerializer):
    sermons_count = serializers.IntegerField(source="sermons.count", read_only=True)

    class Meta:
        model = SermonSeries
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "cover_image",
            "start_date",
            "end_date",
            "sermons_count",
            "is_featured",
        ]


class SermonSerializer(serializers.ModelSerializer):
    series_title = serializers.CharField(source="series.title", read_only=True)

    class Meta:
        model = Sermon
        fields = [
            "id",
            "title",
            "slug",
            "series",
            "series_title",
            "speaker_name",
            "scripture_reference",
            "preached_date",
            "summary",
            "cover_image",
            "audio_file",
            "video_url",
            "audio_duration_seconds",
            "play_count",
            "download_count",
            "is_featured",
        ]
