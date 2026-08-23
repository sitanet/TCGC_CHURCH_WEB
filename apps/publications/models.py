"""
Models for Journals, Bulletins, Study Guides, Devotionals, and Downloadable Resources.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import publication_pdf_upload_path
from apps.core.validators import validate_image_file, validate_pdf_file


class PublicationType(models.TextChoices):
    JOURNAL = "journal", _("Journal")
    NEWSLETTER = "newsletter", _("Newsletter")
    EBOOK = "ebook", _("E-book / Book")
    STUDY_MATERIAL = "study_material", _("Study Material / Outline")
    CONFERENCE_MATERIAL = "conference_material", _("Conference Material")
    BROCHURE = "brochure", _("Brochure / Leaflet")
    REPORT = "report", _("Annual / Ministry Report")
    RESOURCE = "resource", _("Other Downloadable Resource")


class PublicationCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("Publication Category")
        verbose_name_plural = _("Publication Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Publication(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Downloadable church publication (Journals, Newsletters, E-books, Study Outlines).
    """
    title = models.CharField(_("publication title"), max_length=200)
    publication_type = models.CharField(
        _("publication type"),
        max_length=30,
        choices=PublicationType.choices,
        default=PublicationType.JOURNAL,
        db_index=True,
    )
    edition_volume = models.CharField(
        _("edition / volume / issue"),
        max_length=100,
        blank=True,
        help_text="e.g. Vol 4 Issue 2, 2026 Edition, Q1 Journal",
    )
    category = models.ForeignKey(
        PublicationCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publications",
    )
    author_name = models.CharField(_("author / contributor"), max_length=150, default="The CityGate Pastoral Team")
    description = models.TextField(_("summary / editorial description"), blank=True)
    publication_date = models.DateField(_("publication date"), null=True, blank=True, db_index=True)
    
    cover_image = models.ImageField(
        _("cover image"),
        upload_to="publications/covers/",
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    pdf_file = models.FileField(
        _("PDF document file"),
        upload_to=publication_pdf_upload_path,
        validators=[validate_pdf_file],
    )
    file_size_bytes = models.BigIntegerField(_("file size bytes"), default=0)
    is_downloadable = models.BooleanField(_("allow public download"), default=True)
    download_count = models.PositiveIntegerField(_("total downloads"), default=0)

    class Meta:
        verbose_name = _("Publication / Journal")
        verbose_name_plural = _("Publications & Journals")
        ordering = ["-publication_date", "-created_at"]

    def __str__(self):
        type_lbl = self.get_publication_type_display()
        if self.edition_volume:
            return f"[{type_lbl}] {self.title} ({self.edition_volume})"
        return f"[{type_lbl}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        # Capture file size
        if self.pdf_file and hasattr(self.pdf_file, "size"):
            try:
                self.file_size_bytes = self.pdf_file.size
            except Exception:
                pass
        super().save(*args, **kwargs)
