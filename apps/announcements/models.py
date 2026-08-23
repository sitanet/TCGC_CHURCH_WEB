"""
Models for Church Announcements and Header Notification Banners.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class AnnouncementPriority(models.TextChoices):
    NORMAL = "normal", _("Normal")
    IMPORTANT = "important", _("Important")
    URGENT = "urgent", _("Urgent / Emergency")


class Announcement(TimeStampedModel):
    """
    Public announcement or top-bar alert.
    """
    title = models.CharField(_("headline / title"), max_length=200)
    message = models.TextField(_("announcement text"))
    link_url = models.URLField(_("action link URL"), blank=True)
    link_label = models.CharField(_("button label"), max_length=60, default="Learn More", blank=True)
    
    priority = models.CharField(
        _("priority"),
        max_length=20,
        choices=AnnouncementPriority.choices,
        default=AnnouncementPriority.NORMAL,
    )
    show_banner = models.BooleanField(_("show in top notification banner"), default=False)
    is_active = models.BooleanField(_("is currently active"), default=True)
    
    expires_at = models.DateTimeField(_("expiration date & time"), blank=True, null=True)

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return self.title
