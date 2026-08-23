"""
Abstract and shared models for The CityGate Church platform.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    `created_at` and `updated_at` fields.
    """
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SluggedModel(models.Model):
    """
    Abstract base model that provides an auto-generated unique slug.
    """
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def generate_unique_slug(self, source_text: str) -> str:
        """Generate a unique slug based on source text."""
        base_slug = slugify(source_text)[:240]
        if not base_slug:
            base_slug = f"item-{uuid.uuid4().hex[:8]}"
        
        unique_slug = base_slug
        model_class = self.__class__
        counter = 1
        
        while model_class.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
            
        return unique_slug


class PublishableStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    SCHEDULED = "scheduled", _("Scheduled")
    ARCHIVED = "archived", _("Archived")


class PublishableModel(models.Model):
    """
    Abstract base model providing publication workflow fields.
    """
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=PublishableStatus.choices,
        default=PublishableStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True, db_index=True)
    is_featured = models.BooleanField(_("featured"), default=False, db_index=True)

    class Meta:
        abstract = True

    @property
    def is_published(self) -> bool:
        return self.status == PublishableStatus.PUBLISHED


class SEOModel(models.Model):
    """
    Abstract base model providing search engine optimization metadata.
    """
    meta_title = models.CharField(_("meta title"), max_length=160, blank=True)
    meta_description = models.TextField(_("meta description"), max_length=320, blank=True)
    meta_keywords = models.CharField(_("meta keywords"), max_length=255, blank=True)
    canonical_url = models.URLField(_("canonical URL"), blank=True)
    og_image = models.ImageField(_("OpenGraph social image"), upload_to="seo/og_images/", blank=True, null=True)
    no_index = models.BooleanField(_("do not index in search engines"), default=False)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """
    Abstract base model providing custom display ordering.
    """
    sort_order = models.PositiveIntegerField(_("sort order"), default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["sort_order"]


class SiteConfiguration(TimeStampedModel):
    """
    Singleton model for global church details, contact information,
    brand identity, and service times.
    """
    site_name = models.CharField(_("church name"), max_length=200, default="The CityGate Church")
    tagline = models.CharField(
        _("tagline"),
        max_length=300,
        default="A place of divine encounter, spiritual growth, and kingdom impact.",
    )
    logo = models.ImageField(_("primary logo"), upload_to="branding/", blank=True, null=True)
    logo_dark = models.ImageField(_("dark mode / light text logo"), upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(_("favicon"), upload_to="branding/", blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(_("general email"), default="contact@thecitygatechurch.org")
    phone_primary = models.CharField(_("primary phone"), max_length=50, blank=True, default="+234 000 000 0000")
    phone_secondary = models.CharField(_("secondary phone"), max_length=50, blank=True)
    address_line_1 = models.CharField(_("address line 1"), max_length=255, blank=True)
    address_line_2 = models.CharField(_("address line 2"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state/province"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, default="Nigeria")
    
    # Service Schedules (Public overview)
    sunday_service_times = models.CharField(_("Sunday service times"), max_length=200, default="8:00 AM & 10:30 AM")
    midweek_service_times = models.CharField(_("Midweek service times"), max_length=200, default="Wednesdays at 6:00 PM")
    
    # Social & Media Handles
    youtube_url = models.URLField(_("YouTube channel URL"), blank=True)
    facebook_url = models.URLField(_("Facebook page URL"), blank=True)
    instagram_url = models.URLField(_("Instagram profile URL"), blank=True)
    twitter_x_url = models.URLField(_("X / Twitter profile URL"), blank=True)
    live_stream_url = models.URLField(_("Default Live Stream URL"), blank=True)
    
    # Giving Information
    giving_text = models.TextField(_("giving instructions & bank info"), blank=True)

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Guarantee singleton pattern
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
