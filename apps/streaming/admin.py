from django.contrib import admin
from .models import LiveStreamChannel


@admin.register(LiveStreamChannel)
class LiveStreamChannelAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "is_live", "current_topic", "current_speaker", "next_broadcast_time")
    list_editable = ("is_live",)
