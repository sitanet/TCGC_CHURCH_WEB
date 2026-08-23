"""
Models for Church Events, Calendar, Special Services, and Registrations.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import event_banner_upload_path
from apps.core.validators import validate_image_file


class EventCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)

    class Meta:
        verbose_name = _("Event Category")
        verbose_name_plural = _("Event Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Event(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Church event, seminar, revival meeting, or special service.
    """
    title = models.CharField(_("event title"), max_length=200)
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    ministry = models.ForeignKey(
        "ministries.Ministry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("organizing ministry"),
    )
    speaker = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name=_("featured speaker / minister"),
    )
    speaker_name = models.CharField(_("speaker name override"), max_length=150, blank=True)
    
    tagline = models.CharField(_("short tagline"), max_length=255, blank=True)
    description = models.TextField(_("event description"), blank=True)
    banner_image = models.ImageField(
        _("banner flyer / poster"),
        upload_to=event_banner_upload_path,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    banner_image_url = models.URLField(_("external banner image URL"), blank=True)
    
    # Timing & Location
    start_datetime = models.DateTimeField(_("start date and time"), db_index=True)
    end_datetime = models.DateTimeField(_("end date and time"), blank=True, null=True)
    is_recurring = models.BooleanField(_("recurring event"), default=False)
    recurrence_rule = models.CharField(_("recurrence description"), max_length=100, blank=True, help_text="e.g. Every 1st Sunday")
    
    venue_name = models.CharField(_("venue / location name"), max_length=200, default="The CityGate Main Auditorium")
    venue_address = models.CharField(_("venue address"), max_length=255, blank=True)
    location = models.ForeignKey(
        "ministries.ChurchLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    is_online = models.BooleanField(_("online stream available"), default=True)
    stream_link = models.URLField(_("live stream link"), blank=True)

    # Registration & Attendance
    requires_registration = models.BooleanField(_("requires registration"), default=False)
    registration_url = models.URLField(_("external registration URL (if any)"), blank=True)
    max_attendees = models.PositiveIntegerField(_("max attendee capacity"), blank=True, null=True)
    is_free = models.BooleanField(_("is free event"), default=True)
    contact_email = models.EmailField(_("inquiry email"), blank=True)
    contact_phone = models.CharField(_("inquiry phone"), max_length=50, blank=True)

    class Meta:
        verbose_name = _("Church Event")
        verbose_name_plural = _("Church Events")
        ordering = ["start_datetime"]

    def __str__(self):
        return f"{self.title} ({self.start_datetime.strftime('%b %d, %Y')})"

    @property
    def banner_image_display_url(self) -> str:
        if self.banner_image:
            try:
                return self.banner_image.url
            except Exception:
                pass
        return self.banner_image_url or ""

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def get_speaker_display(self) -> str:
        if self.speaker:
            return self.speaker.name
        return self.speaker_name or ""


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
