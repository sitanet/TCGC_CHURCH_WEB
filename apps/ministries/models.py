"""
Models for Ministries and Community Groups.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel
from apps.people.models import Person


class Ministry(TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel):
    """
    Church ministry (e.g. Children Church, Youth, Men of Valour, Women of Destiny, Worship, Protocol).
    """
    name = models.CharField(_("ministry name"), max_length=150)
    tagline = models.CharField(_("short tagline"), max_length=255, blank=True)
    description = models.TextField(_("detailed description"), blank=True)
    icon_name = models.CharField(_("feather/tabler icon name"), max_length=50, blank=True, help_text="e.g. heart, users, book-open")
    cover_image = models.ImageField(_("cover image"), upload_to="ministries/covers/", blank=True, null=True)
    leader = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_ministries")
    
    # Meeting details
    meeting_schedule = models.CharField(_("meeting schedule"), max_length=200, blank=True, help_text="e.g. Every 2nd Saturday at 4 PM")
    meeting_location = models.CharField(_("meeting location"), max_length=200, blank=True)
    contact_email = models.EmailField(_("ministry contact email"), blank=True)
    
    # Engagement
    accepts_volunteers = models.BooleanField(_("accepts volunteers"), default=True)

    class Meta:
        verbose_name = _("Ministry")
        verbose_name_plural = _("Ministries")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)
