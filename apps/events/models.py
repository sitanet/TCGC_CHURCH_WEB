"""
Models for Church Events, Special Services, and Registrations.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import event_banner_upload_path


class EventCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)

    class Meta:
        verbose_name = _("Event Category")
        verbose_name_plural = _("Event Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Event(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Church event, seminar, or special service.
    """
    title = models.CharField(_("event title"), max_length=200)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    tagline = models.CharField(_("short tagline"), max_length=255, blank=True)
    description = models.TextField(_("event description"), blank=True)
    banner_image = models.ImageField(_("banner flyer / image"), upload_to=event_banner_upload_path, blank=True, null=True)
    
    # Timing & Location
    start_datetime = models.DateTimeField(_("start date and time"), db_index=True)
    end_datetime = models.DateTimeField(_("end date and time"), blank=True, null=True)
    is_recurring = models.BooleanField(_("recurring event"), default=False)
    recurrence_rule = models.CharField(_("recurrence description"), max_length=100, blank=True, help_text="e.g. Every Sunday")
    
    venue_name = models.CharField(_("venue / location name"), max_length=200, default="The CityGate Main Auditorium")
    venue_address = models.CharField(_("venue address"), max_length=255, blank=True)
    is_online = models.BooleanField(_("online stream available"), default=True)
    stream_link = models.URLField(_("live stream link"), blank=True)

    # Registration
    requires_registration = models.BooleanField(_("requires registration"), default=False)
    max_attendees = models.PositiveIntegerField(_("max attendees"), blank=True, null=True)
    is_free = models.BooleanField(_("is free event"), default=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["start_datetime"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)


class EventRegistration(TimeStampedModel):
    """
    User registration for events.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    full_name = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("email address"))
    phone = models.CharField(_("phone number"), max_length=50)
    notes = models.TextField(_("additional notes"), blank=True)
    is_confirmed = models.BooleanField(_("is confirmed"), default=True)

    class Meta:
        verbose_name = _("Event Registration")
        verbose_name_plural = _("Event Registrations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} -> {self.event.title}"
