from django.contrib import admin
from .models import Conference, ConferenceSpeaker, ConferenceSession


class ConferenceSessionInline(admin.TabularInline):
    model = ConferenceSession
    extra = 2


class ConferenceSpeakerInline(admin.TabularInline):
    model = ConferenceSpeaker
    extra = 2


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "start_date", "end_date", "status", "is_featured")
    list_filter = ("status", "is_featured", "start_date")
    search_fields = ("title", "theme", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ConferenceSpeakerInline, ConferenceSessionInline]
