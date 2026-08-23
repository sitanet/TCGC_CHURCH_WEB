"""
Models for Ministries, Community Groups, Recurring Meetings, and Campus Locations.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel
from apps.people.models import Person
from apps.core.validators import validate_image_file


class DayOfWeek(models.IntegerChoices):
    MONDAY = 1, _("Monday")
    TUESDAY = 2, _("Tuesday")
    WEDNESDAY = 3, _("Wednesday")
    THURSDAY = 4, _("Thursday")
    FRIDAY = 5, _("Friday")
    SATURDAY = 6, _("Saturday")
    SUNDAY = 7, _("Sunday")


class ChurchLocation(TimeStampedModel, SluggedModel, OrderedModel):
    """
    Physical church campuses and center locations.
    """
    name = models.CharField(_("campus / center name"), max_length=150)
    address = models.CharField(_("street address"), max_length=255)
    city = models.CharField(_("city"), max_length=100, default="Lagos")
    state = models.CharField(_("state"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, default="Nigeria")
    is_main_campus = models.BooleanField(_("is main headquarters campus"), default=False)
    phone = models.CharField(_("contact phone"), max_length=50, blank=True)
    email = models.EmailField(_("campus email"), blank=True)
    google_maps_url = models.URLField(_("Google Maps URL / directions"), blank=True)
    photo = models.ImageField(
        _("campus photo"),
        upload_to="locations/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Church Location")
        verbose_name_plural = _("Church Locations")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.city})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Ministry(TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel):
    """
    Church ministry (e.g. Children Church, Youth, Men of Valour, Women of Destiny, Worship, Protocol).
    """
    name = models.CharField(_("ministry name"), max_length=150)
    tagline = models.CharField(_("short tagline"), max_length=255, blank=True)
    description = models.TextField(_("detailed description"), blank=True)
    icon_name = models.CharField(_("feather/tabler icon name"), max_length=50, blank=True, help_text="e.g. heart, users, book-open")
    cover_image = models.ImageField(
        _("cover image"),
        upload_to="ministries/covers/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    leader = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name="led_ministries")
    
    # Meeting details
    meeting_schedule = models.CharField(_("meeting schedule"), max_length=200, blank=True, help_text="e.g. Every 2nd Saturday at 4 PM")
    meeting_location = models.CharField(_("meeting location"), max_length=200, blank=True)
    contact_email = models.EmailField(_("ministry contact email"), blank=True)
    contact_phone = models.CharField(_("ministry contact phone"), max_length=50, blank=True)
    
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


class ChurchMeeting(TimeStampedModel, SluggedModel, OrderedModel):
    """
    Recurring church service or fellowship meeting.
    """
    name = models.CharField(_("meeting name"), max_length=150, help_text="e.g. Sunday 1st Service, Midweek Communion, Prayer Watch")
    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meetings",
        verbose_name=_("associated ministry"),
    )
    location = models.ForeignKey(
        ChurchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meetings",
        verbose_name=_("campus location"),
    )
    day_of_week = models.IntegerField(_("day of the week"), choices=DayOfWeek.choices, default=DayOfWeek.SUNDAY)
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"), blank=True, null=True)
    location_hall = models.CharField(_("auditorium / hall room"), max_length=150, default="Main Auditorium")
    
    is_online = models.BooleanField(_("broadcasted online"), default=True)
    stream_link = models.URLField(_("stream link URL"), blank=True)
    description = models.TextField(_("meeting description / what to expect"), blank=True)
    is_active = models.BooleanField(_("is actively running"), default=True)

    class Meta:
        verbose_name = _("Church Meeting / Service")
        verbose_name_plural = _("Church Meetings & Services")
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.name} — {self.get_day_of_week_display()} ({self.start_time:%H:%M})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)
