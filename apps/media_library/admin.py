from django.contrib import admin
from .models import MediaCategory, MediaAsset, PhotoGallery, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3


@admin.register(PhotoGallery)
class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "status", "created_at")
    list_filter = ("status", "event_date")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GalleryImageInline]


@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "category", "file_size_bytes", "status", "created_at")
    list_filter = ("media_type", "status", "category")
    search_fields = ("title", "tags", "alt_text")
