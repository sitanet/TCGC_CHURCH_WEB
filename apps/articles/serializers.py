"""
Serializers for articles.
"""
from rest_framework import serializers
from .models import Article, ArticleCategory


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ["id", "name", "slug"]


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="display_author", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "category_name",
            "author_name",
            "summary",
            "body",
            "featured_image",
            "reading_time_minutes",
            "view_count",
            "published_at",
            "is_featured",
        ]
