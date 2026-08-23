"""
Models for Church Announcements, Homepage Banners, and Header Alert Notifications.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.core.validators import validate_image_file


class AnnouncementPriority(models.TextChoices):
    NORMAL = "normal", _("Normal")
    IMPORTANT = "important", _("Important")
    URGENT = "urgent", _("Urgent / Emergency")


class Announcement(TimeStampedModel):
    """
    Public announcement, popup notice, or top-bar alert banner.
    """
    title = models.CharField(_("headline / title"), max_length=200)
    message = models.TextField(_("announcement text"))
    image = models.ImageField(
        _("announcement flyer / photo"),
        upload_to="announcements/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    link_url = models.URLField(_("action link URL"), blank=True)
    link_label = models.CharField(_("button label"), max_length=60, default="Learn More", blank=True)
    
    priority = models.CharField(
        _("priority"),
        max_length=20,
        choices=AnnouncementPriority.choices,
        default=AnnouncementPriority.NORMAL,
    )
    show_banner = models.BooleanField(_("show in top notification banner"), default=False)
    show_homepage = models.BooleanField(_("show prominently on homepage"), default=True)
    is_active = models.BooleanField(_("is currently active"), default=True)
    
    start_date = models.DateTimeField(_("start display date & time"), blank=True, null=True)
    expires_at = models.DateTimeField(_("expiration date & time"), blank=True, null=True)

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return self.title
