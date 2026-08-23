"""
Models for Annual Conferences, Conventions, and Multi-Day Summits.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import get_upload_path
from apps.people.models import Person


class Conference(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Major annual conference (e.g. Believers Convention, Leadership Summit).
    """
    title = models.CharField(_("conference title"), max_length=200)
    theme = models.CharField(_("conference theme / motto"), max_length=255)
    description = models.TextField(_("detailed description"), blank=True)
    banner_image = models.ImageField(_("main banner"), upload_to="conferences/banners/", blank=True, null=True)
    
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    venue = models.CharField(_("venue"), max_length=255, default="The CityGate Main Auditorium")
    
    registration_link = models.URLField(_("registration URL"), blank=True)
    schedule_document = models.FileField(_("program schedule PDF"), upload_to="conferences/docs/", blank=True, null=True)

    class Meta:
        verbose_name = _("Conference")
        verbose_name_plural = _("Conferences")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} — {self.theme}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)


class ConferenceSpeaker(TimeStampedModel):
    """
    Guest and resident speakers for a specific conference.
    """
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="speakers")
    speaker = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="conference_appearances")
    name_override = models.CharField(_("speaker name (if not in people directory)"), max_length=150, blank=True)
    title_override = models.CharField(_("ministry title / organization"), max_length=150, blank=True)
    photo_override = models.ImageField(_("photo override"), upload_to="conferences/speakers/", blank=True, null=True)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("Conference Speaker")
        verbose_name_plural = _("Conference Speakers")
        ordering = ["sort_order"]

    def __str__(self):
        return self.name_override or (self.speaker.name if self.speaker else "Unknown Speaker")


class ConferenceSession(TimeStampedModel):
    """
    Specific session/breakout within a conference schedule.
    """
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="sessions")
    session_title = models.CharField(_("session title"), max_length=200)
    speaker_info = models.CharField(_("minister / speaker"), max_length=150, blank=True)
    session_date = models.DateField(_("session date"))
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"), blank=True, null=True)
    location_hall = models.CharField(_("hall / room"), max_length=100, blank=True)
    description = models.TextField(_("session notes / synopsis"), blank=True)

    class Meta:
        verbose_name = _("Conference Session")
        verbose_name_plural = _("Conference Sessions")
        ordering = ["session_date", "start_time"]

    def __str__(self):
        return f"{self.session_title} ({self.session_date})"
