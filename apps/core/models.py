"""
Abstract and shared models for The CityGate Church platform.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
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
    scheduled_at = models.DateTimeField(_("scheduled publication time"), null=True, blank=True, db_index=True)
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
    sort_order = models.PositiveIntegerField(_("sort order"), default=0, blank=True, db_index=True)

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
    church_vision_short = models.TextField(_("short vision statement"), blank=True)
    logo = models.ImageField(_("primary logo"), upload_to="branding/", blank=True, null=True)
    logo_dark = models.ImageField(_("dark mode / light text logo"), upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(_("favicon"), upload_to="branding/", blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(_("general email"), default="contact@thecitygatechurch.org")
    phone_primary = models.CharField(_("primary phone"), max_length=50, blank=True, default="+234 000 000 0000")
    phone_secondary = models.CharField(_("secondary phone"), max_length=50, blank=True)
    address_line_1 = models.CharField(_("address line 1"), max_length=255, blank=True)
    address_line_2 = models.CharField(_("address line 2"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True, default="Lagos")
    state = models.CharField(_("state/province"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, default="Nigeria")
    google_maps_embed_url = models.URLField(_("Google Maps Embed URL"), blank=True)
    
    # Service Schedules
    sunday_service_times = models.CharField(_("Sunday service times"), max_length=200, default="8:00 AM & 10:30 AM")
    midweek_service_times = models.CharField(_("Midweek service times"), max_length=200, default="Wednesdays at 6:00 PM")
    prayer_meeting_times = models.CharField(_("Prayer gathering times"), max_length=200, default="Fridays at 6:00 PM")
    
    # Social & Media Handles
    youtube_url = models.URLField(_("YouTube channel URL"), blank=True)
    facebook_url = models.URLField(_("Facebook page URL"), blank=True)
    instagram_url = models.URLField(_("Instagram profile URL"), blank=True)
    twitter_x_url = models.URLField(_("X / Twitter profile URL"), blank=True)
    telegram_url = models.URLField(_("Telegram channel URL"), blank=True)
    tiktok_url = models.URLField(_("TikTok URL"), blank=True)
    live_stream_url = models.URLField(_("Default Live Stream URL"), blank=True)
    
    # SEO Defaults
    default_meta_title = models.CharField(_("default SEO meta title"), max_length=160, blank=True)
    default_meta_description = models.TextField(_("default SEO meta description"), max_length=320, blank=True)
    default_og_image = models.ImageField(_("default social sharing OG image"), upload_to="branding/", blank=True, null=True)

    # Giving & Footer Information
    giving_text = models.TextField(_("giving instructions & bank info"), blank=True)
    footer_text = models.TextField(_("footer brief narrative"), blank=True)
    copyright_override = models.CharField(_("custom copyright text"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomepageConfig(TimeStampedModel):
    """
    Singleton model for configuring dynamic homepage hero,
    action buttons, and featured showcase content items.
    """
    hero_tag = models.CharField(_("hero eyebrow tag"), max_length=100, default="✦ Welcome to The CityGate")
    hero_title = models.CharField(_("hero headline"), max_length=255, default="Where Faith Meets Purpose & Kingdom Power.")
    hero_subtitle = models.TextField(
        _("hero lead text"),
        default="A vibrant community of believers devoted to word-centered truth, spirit-led worship, and transformative impact in our city and across the nations.",
    )
    hero_image = models.ImageField(_("hero banner image"), upload_to="homepage/", blank=True, null=True)
    hero_video_url = models.URLField(_("hero background / preview video URL"), blank=True)
    
    # Primary & Secondary Call to Actions
    primary_cta_text = models.CharField(_("primary button label"), max_length=60, default="Plan Your Visit")
    primary_cta_link = models.CharField(_("primary button link"), max_length=255, default="/visit/")
    secondary_cta_text = models.CharField(_("secondary button label"), max_length=60, default="Our Beliefs & Story")
    secondary_cta_link = models.CharField(_("secondary button link"), max_length=255, default="/about/")
    
    # Service times card in Hero
    service_banner_title = models.CharField(_("service banner title"), max_length=150, default="Join Us This Sunday")
    service_banner_desc = models.CharField(
        _("service banner short text"),
        max_length=255,
        default="Experience deep worship, prophetic insight, and practical biblical teachings.",
    )
    service_banner_times = models.CharField(_("service banner times"), max_length=150, default="1st Service: 8:00 AM | 2nd Service: 10:30 AM")

    # Dynamic Showcase Selection (FKs to content models)
    featured_teaching = models.ForeignKey("teachings.Sermon", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    featured_event = models.ForeignKey("events.Event", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    featured_conference = models.ForeignKey("conferences.Conference", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    featured_publication = models.ForeignKey("publications.Publication", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    featured_article = models.ForeignKey("articles.Article", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    class Meta:
        verbose_name = _("Homepage Configuration")
        verbose_name_plural = _("Homepage Configuration")

    def __str__(self):
        return "Homepage Content Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ActivityLog(models.Model):
    """
    Audit log tracking all important staff operations on the CMS.
    """
    class Action(models.TextChoices):
        CREATED = "created", _("Created")
        UPDATED = "updated", _("Updated")
        DELETED = "deleted", _("Deleted")
        PUBLISHED = "published", _("Published")
        UNPUBLISHED = "unpublished", _("Unpublished")
        ARCHIVED = "archived", _("Archived")
        UPLOADED = "uploaded", _("Uploaded")
        DOWNLOADED = "downloaded", _("Downloaded")
        LOGIN = "login", _("User Login")
        STATUS_CHANGE = "status_change", _("Status Changed")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    action = models.CharField(_("action"), max_length=30, choices=Action.choices)
    model_name = models.CharField(_("module / model"), max_length=100)
    object_id = models.CharField(_("object ID"), max_length=100, blank=True)
    object_repr = models.CharField(_("object name / title"), max_length=255, blank=True)
    details = models.TextField(_("details"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), blank=True, null=True)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("Activity Log")
        verbose_name_plural = _("Activity Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        user_name = self.user.username if self.user else "System"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user_name} {self.action} {self.model_name}: {self.object_repr}"


def log_activity(user, action: str, instance=None, details: str = "", request=None, model_name: str = "", object_id: str = "", object_repr: str = ""):
    """
    Safe helper function to record an administrator activity log.
    """
    try:
        ip = None
        if request:
            x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = x_forwarded.split(",")[0] if x_forwarded else request.META.get("REMOTE_ADDR")

        m_name = model_name
        obj_id = object_id
        obj_repr = object_repr

        if instance is not None:
            m_name = m_name or instance.__class__.__name__
            obj_id = obj_id or str(getattr(instance, "pk", ""))
            obj_repr = obj_repr or str(instance)[:250]

        ActivityLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            model_name=m_name,
            object_id=obj_id,
            object_repr=obj_repr,
            details=details,
            ip_address=ip,
        )
    except Exception as e:
        # Non-blocking error logging
        pass
