from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "show_banner", "is_active", "expires_at", "created_at")
    list_filter = ("priority", "show_banner", "is_active")
    search_fields = ("title", "message")
