"""
Models for tracking platform traffic, sermon listens, and document downloads.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class PageHit(TimeStampedModel):
    """
    Lightweight page visit counter.
    """
    path = models.CharField(_("page path"), max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(_("visitor IP"), blank=True, null=True)
    user_agent = models.CharField(_("user agent"), max_length=255, blank=True)
    referrer = models.URLField(_("referrer URL"), blank=True)

    class Meta:
        verbose_name = _("Page Hit")
        verbose_name_plural = _("Page Hits")
        ordering = ["-created_at"]


class MediaPlayEvent(TimeStampedModel):
    """
    Telemetry event when a sermon audio/video is played.
    """
    content_title = models.CharField(_("content title"), max_length=255)
    content_type = models.CharField(_("content type"), max_length=50, default="sermon")
    content_id = models.PositiveIntegerField(_("content ID"), default=0)
    duration_played_seconds = models.PositiveIntegerField(_("duration played (seconds)"), default=0)

    class Meta:
        verbose_name = _("Media Play Event")
        verbose_name_plural = _("Media Play Events")
        ordering = ["-created_at"]


class DownloadEvent(TimeStampedModel):
    """
    Telemetry event when a publication PDF or resource is downloaded.
    """
    resource_title = models.CharField(_("resource title"), max_length=255)
    resource_type = models.CharField(_("resource type"), max_length=50, default="publication")
    resource_id = models.PositiveIntegerField(_("resource ID"), default=0)

    class Meta:
        verbose_name = _("Download Event")
        verbose_name_plural = _("Download Events")
        ordering = ["-created_at"]
