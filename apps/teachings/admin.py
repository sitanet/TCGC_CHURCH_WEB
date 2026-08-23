from django.contrib import admin
from .models import Sermon, SermonSeries


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "is_featured", "created_at")
    list_filter = ("status", "is_featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ("title", "series", "speaker_name", "preached_date", "status", "play_count", "is_featured")
    list_filter = ("status", "is_featured", "preached_date", "series")
    search_fields = ("title", "speaker_name", "scripture_reference", "summary")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "preached_date"
