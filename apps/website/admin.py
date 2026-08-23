from django.contrib import admin
from .models import ContactMessage, PrayerRequest, NewsletterSubscriber


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "subject", "message")


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "status", "handled_by", "created_at")
    list_filter = ("status", "is_confidential", "created_at")
    search_fields = ("full_name", "prayer_point")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email", "full_name")
