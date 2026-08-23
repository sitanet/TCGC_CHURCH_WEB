"""
Serializers for publications.
"""
from rest_framework import serializers
from .models import Publication, PublicationCategory


class PublicationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationCategory
        fields = ["id", "name", "slug", "description"]


class PublicationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    publication_type_display = serializers.CharField(source="get_publication_type_display", read_only=True)

    class Meta:
        model = Publication
        fields = [
            "id",
            "title",
            "slug",
            "publication_type",
            "publication_type_display",
            "edition_volume",
            "category",
            "category_name",
            "author_name",
            "description",
            "publication_date",
            "cover_image",
            "pdf_file",
            "file_size_bytes",
            "is_downloadable",
            "download_count",
            "status",
            "is_featured",
            "created_at",
        ]
