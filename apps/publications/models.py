"""
Models for Bulletins, Study Guides, Devotionals, and Downloadable Resources.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import publication_pdf_upload_path


class PublicationCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)

    class Meta:
        verbose_name = _("Publication Category")
        verbose_name_plural = _("Publication Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Publication(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Downloadable church publication (e.g. Monthly Devotional, Study Outline, Annual Report).
    """
    title = models.CharField(_("publication title"), max_length=200)
    category = models.ForeignKey(PublicationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="publications")
    author_name = models.CharField(_("author name"), max_length=150, default="The CityGate Pastoral Team")
    description = models.TextField(_("summary / description"), blank=True)
    cover_image = models.ImageField(_("cover image"), upload_to="publications/covers/", blank=True, null=True)
    pdf_file = models.FileField(_("PDF document file"), upload_to=publication_pdf_upload_path)
    file_size_bytes = models.BigIntegerField(_("file size bytes"), default=0)
    download_count = models.PositiveIntegerField(_("total downloads"), default=0)

    class Meta:
        verbose_name = _("Publication")
        verbose_name_plural = _("Publications & Downloads")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)
