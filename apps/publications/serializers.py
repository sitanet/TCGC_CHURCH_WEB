"""
Serializers for publications.
"""
from rest_framework import serializers
from .models import Publication, PublicationCategory


class PublicationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationCategory
        fields = ["id", "name", "slug"]


class PublicationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Publication
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "category_name",
            "author_name",
            "description",
            "cover_image",
            "pdf_file",
            "file_size_bytes",
            "download_count",
            "created_at",
            "is_featured",
        ]
