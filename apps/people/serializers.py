"""
Serializers for people app.
"""
from rest_framework import serializers
from .models import LeadershipCategory, Person


class LeadershipCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadershipCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class PersonSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Person
        fields = [
            "id",
            "name",
            "slug",
            "title",
            "category",
            "category_name",
            "photo",
            "biography",
            "email",
            "phone",
            "twitter_handle",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "sort_order",
            "is_featured",
        ]
