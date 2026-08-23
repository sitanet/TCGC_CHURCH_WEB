from django.contrib import admin
from .models import SiteConfiguration, HomepageConfig, ActivityLog


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone_primary", "city", "updated_at")


@admin.register(HomepageConfig)
class HomepageConfigAdmin(admin.ModelAdmin):
    list_display = ("hero_title", "updated_at")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr", "ip_address")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("object_repr", "details", "user__username")
