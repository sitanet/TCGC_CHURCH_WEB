"""
Serializers for teachings application.
"""
from rest_framework import serializers
from .models import Sermon, SermonSeries, SermonCategory, SermonScripture


class SermonScriptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonScripture
        fields = ["id", "book", "chapter", "verse_start", "verse_end", "scripture_text", "sort_order"]


class SermonCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonCategory
        fields = ["id", "name", "slug", "description"]


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
    category_name = serializers.CharField(source="category.name", read_only=True)
    speaker_display = serializers.CharField(source="get_speaker_display", read_only=True)
    scriptures = SermonScriptureSerializer(many=True, read_only=True)

    class Meta:
        model = Sermon
        fields = [
            "id",
            "title",
            "slug",
            "series",
            "series_title",
            "category",
            "category_name",
            "speaker",
            "speaker_name",
            "speaker_display",
            "scripture_reference",
            "preached_date",
            "summary",
            "study_notes",
            "transcript_text",
            "transcript_file",
            "cover_image",
            "audio_file",
            "video_file",
            "video_url",
            "video_embed_code",
            "audio_duration_seconds",
            "play_count",
            "download_count",
            "status",
            "is_featured",
            "scriptures",
        ]
