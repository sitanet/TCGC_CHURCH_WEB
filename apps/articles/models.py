"""
Models for Articles, Announcements, News, and Pastoral Messages.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.accounts.models import User
from apps.core.validators import validate_image_file


class ArticleCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("Article Category")
        verbose_name_plural = _("Article Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Article(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Editorial blog post, journal piece, or pastoral article.
    """
    title = models.CharField(_("article title"), max_length=255)
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    author_name_override = models.CharField(_("author name (if not a registered user)"), max_length=150, blank=True)
    
    summary = models.TextField(_("excerpt / short summary"), max_length=500, blank=True)
    body = models.TextField(_("article content (HTML / Markdown)"), blank=True)
    featured_image = models.ImageField(
        _("featured image"),
        upload_to="articles/images/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    tags = models.CharField(_("tags (comma separated)"), max_length=255, blank=True)
    reading_time_minutes = models.PositiveIntegerField(_("estimated reading time (mins)"), default=3)
    view_count = models.PositiveIntegerField(_("view count"), default=0)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles & News")
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        # Auto-calculate reading time if body has text
        if self.body:
            words = len(self.body.split())
            self.reading_time_minutes = max(1, round(words / 200))
        super().save(*args, **kwargs)

    @property
    def display_author(self) -> str:
        if self.author_name_override:
            return self.author_name_override
        if self.author:
            return self.author.get_full_name() or self.author.username
        return "The CityGate Church"
