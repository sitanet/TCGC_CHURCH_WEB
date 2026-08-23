"""
Serializers for media_library.
"""
from rest_framework import serializers
from .models import MediaCategory, MediaAsset, PhotoGallery, GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ["id", "image", "caption", "sort_order"]


class PhotoGallerySerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)
    images_count = serializers.IntegerField(source="images.count", read_only=True)

    class Meta:
        model = PhotoGallery
        fields = ["id", "title", "slug", "event_date", "description", "cover_image", "images_count", "images"]


class MediaAssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MediaAsset
        fields = ["id", "title", "media_type", "category", "category_name", "file", "file_size_bytes", "alt_text", "tags", "created_at"]
