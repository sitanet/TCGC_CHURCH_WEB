from django.contrib import admin
from .models import PublicationCategory, Publication


@admin.register(PublicationCategory)
class PublicationCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author_name", "download_count", "status", "is_featured", "created_at")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("title", "author_name", "description")
    prepopulated_fields = {"slug": ("title",)}
