"""
Models for Live Streaming status, YouTube/Facebook feeds, and Countdown.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class StreamPlatform(models.TextChoices):
    YOUTUBE = "youtube", _("YouTube Live")
    FACEBOOK = "facebook", _("Facebook Live")
    CUSTOM_RTMP = "custom_rtmp", _("Custom RTMP / HLS Stream")


class LiveStreamChannel(TimeStampedModel):
    """
    Channel configuration and currently active broadcast.
    """
    title = models.CharField(_("stream title / service name"), max_length=200, default="The CityGate Church Live Service")
    platform = models.CharField(_("platform"), max_length=20, choices=StreamPlatform.choices, default=StreamPlatform.YOUTUBE)
    stream_url = models.URLField(_("live stream URL / Embed URL"), default="https://www.youtube.com/@TheCityGateChurch")
    is_live = models.BooleanField(_("is currently broadcasting LIVE"), default=False)
    
    current_topic = models.CharField(_("current message topic"), max_length=255, blank=True)
    current_speaker = models.CharField(_("current minister / speaker"), max_length=150, blank=True)
    next_broadcast_time = models.DateTimeField(_("next scheduled broadcast"), blank=True, null=True)
    
    offline_poster_image = models.ImageField(_("offline thumbnail poster"), upload_to="streaming/posters/", blank=True, null=True)
    viewer_count = models.PositiveIntegerField(_("approximate live viewers"), default=0)

    class Meta:
        verbose_name = _("Live Stream Channel")
        verbose_name_plural = _("Live Stream Channel")

    def __str__(self):
        status = "🔴 LIVE" if self.is_live else "⚪ Offline"
        return f"{self.title} [{status}]"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
