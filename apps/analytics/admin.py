from django.contrib import admin
from .models import PageHit, MediaPlayEvent, DownloadEvent


@admin.register(PageHit)
class PageHitAdmin(admin.ModelAdmin):
    list_display = ("path", "ip_address", "created_at")
    list_filter = ("created_at",)
    search_fields = ("path", "ip_address")


@admin.register(MediaPlayEvent)
class MediaPlayEventAdmin(admin.ModelAdmin):
    list_display = ("content_title", "content_type", "duration_played_seconds", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("content_title",)


@admin.register(DownloadEvent)
class DownloadEventAdmin(admin.ModelAdmin):
    list_display = ("resource_title", "resource_type", "created_at")
    list_filter = ("resource_type", "created_at")
    search_fields = ("resource_title",)
