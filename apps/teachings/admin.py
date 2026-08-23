from django.contrib import admin
from .models import Sermon, SermonSeries, SermonCategory, SermonScripture


class SermonScriptureInline(admin.TabularInline):
    model = SermonScripture
    extra = 1


@admin.register(SermonCategory)
class SermonCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(SermonSeries)
class SermonSeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "is_featured", "created_at")
    list_filter = ("status", "is_featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ("title", "series", "category", "speaker", "preached_date", "status", "play_count", "is_featured")
    list_filter = ("status", "is_featured", "preached_date", "category", "series")
    search_fields = ("title", "speaker_name", "scripture_reference", "summary")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "preached_date"
    inlines = [SermonScriptureInline]
