"""
Models for Live Streaming status, YouTube/Facebook feeds, and Countdown.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.core.validators import validate_image_file


class StreamPlatform(models.TextChoices):
    YOUTUBE = "youtube", _("YouTube Live")
    FACEBOOK = "facebook", _("Facebook Live")
    CUSTOM_RTMP = "custom_rtmp", _("Custom RTMP / HLS Stream")


class StreamStatus(models.TextChoices):
    LIVE = "live", _("🔴 LIVE NOW")
    OFFLINE = "offline", _("⚪ Offline")
    UPCOMING = "upcoming", _("🟡 Upcoming Broadcast")


class LiveStreamChannel(TimeStampedModel):
    """
    Channel configuration, broadcast switcher, and upcoming program schedule.
    """
    title = models.CharField(_("stream title / service name"), max_length=200, default="The CityGate Church Live Service")
    platform = models.CharField(_("platform"), max_length=20, choices=StreamPlatform.choices, default=StreamPlatform.YOUTUBE)
    stream_status = models.CharField(_("broadcast status"), max_length=20, choices=StreamStatus.choices, default=StreamStatus.OFFLINE)
    is_live = models.BooleanField(_("is currently broadcasting LIVE"), default=False)
    
    stream_url = models.URLField(_("video live stream URL / Embed"), default="https://www.youtube.com/@TheCityGateChurch")
    audio_stream_url = models.URLField(_("audio-only live stream URL (Radio/Shoutcast)"), blank=True)
    
    current_program = models.CharField(_("current program title"), max_length=200, default="Sunday Divine Encounter Service", blank=True)
    current_topic = models.CharField(_("current message topic"), max_length=255, blank=True)
    current_speaker = models.CharField(_("current minister / speaker"), max_length=150, blank=True)
    
    start_time = models.DateTimeField(_("broadcast start time"), null=True, blank=True)
    end_time = models.DateTimeField(_("broadcast end time"), null=True, blank=True)
    
    next_program = models.CharField(_("next upcoming program"), max_length=200, default="Midweek Communion Encounter", blank=True)
    next_broadcast_time = models.DateTimeField(_("next scheduled broadcast"), blank=True, null=True)
    
    offline_poster_image = models.ImageField(
        _("offline thumbnail poster"),
        upload_to="streaming/posters/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    viewer_count = models.PositiveIntegerField(_("approximate live viewers"), default=0)

    class Meta:
        verbose_name = _("Live Stream Channel")
        verbose_name_plural = _("Live Stream Channel")

    def __str__(self):
        return f"{self.title} [{self.get_stream_status_display()}]"

    def save(self, *args, **kwargs):
        self.pk = 1
        # Synchronize is_live with stream_status
        self.is_live = (self.stream_status == StreamStatus.LIVE)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
