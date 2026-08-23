from django.contrib import admin
from .models import Ministry, ChurchMeeting, ChurchLocation


@admin.register(ChurchLocation)
class ChurchLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_main_campus", "sort_order")
    list_filter = ("is_main_campus", "city")
    search_fields = ("name", "address", "city")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name", "leader", "meeting_schedule", "status", "sort_order", "is_featured")
    list_filter = ("status", "accepts_volunteers", "is_featured")
    search_fields = ("name", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ChurchMeeting)
class ChurchMeetingAdmin(admin.ModelAdmin):
    list_display = ("name", "ministry", "day_of_week", "start_time", "location_hall", "is_active", "sort_order")
    list_filter = ("day_of_week", "is_active", "is_online")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
