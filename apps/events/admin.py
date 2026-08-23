from django.contrib import admin
from .models import EventCategory, Event, EventRegistration


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "start_datetime", "venue_name", "status", "is_featured")
    list_filter = ("status", "category", "is_featured", "is_online", "is_recurring")
    search_fields = ("title", "tagline", "venue_name", "description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_datetime"


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "event", "email", "phone", "is_confirmed", "created_at")
    list_filter = ("event", "is_confirmed", "created_at")
    search_fields = ("full_name", "email", "phone")
