from django.contrib import admin
from .models import ArticleCategory, Article


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "display_author", "published_at", "status", "view_count", "is_featured")
    list_filter = ("status", "category", "is_featured", "published_at")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
