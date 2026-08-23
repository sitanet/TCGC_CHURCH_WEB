from django.contrib import admin
from .models import Ministry


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name", "leader", "meeting_schedule", "status", "sort_order", "is_featured")
    list_filter = ("status", "accepts_volunteers", "is_featured")
    search_fields = ("name", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}
