"""
Models for Media Library, Photo Galleries and Digital Assets.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import gallery_photo_upload_path
from apps.core.validators import validate_image_file, validate_file_safety


class MediaType(models.TextChoices):
    IMAGE = "image", _("Image / Photo")
    VIDEO = "video", _("Video")
    AUDIO = "audio", _("Audio Recording")
    DOCUMENT = "document", _("Document / PDF")


class MediaCategory(TimeStampedModel, SluggedModel):
    name = models.CharField(_("category name"), max_length=100)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("Media Category")
        verbose_name_plural = _("Media Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class MediaAsset(TimeStampedModel, PublishableModel):
    """
    Centralized file asset store for images, audio, video, and documents.
    """
    title = models.CharField(_("asset title"), max_length=255)
    media_type = models.CharField(_("media type"), max_length=20, choices=MediaType.choices, default=MediaType.IMAGE, db_index=True)
    category = models.ForeignKey(MediaCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets")
    file = models.FileField(_("media file"), upload_to="media_library/assets/", validators=[validate_file_safety])
    file_size_bytes = models.BigIntegerField(_("file size in bytes"), default=0)
    mime_type = models.CharField(_("MIME type"), max_length=100, blank=True)
    
    # Metadata
    width = models.PositiveIntegerField(_("image width (px)"), null=True, blank=True)
    height = models.PositiveIntegerField(_("image height (px)"), null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(_("media duration (seconds)"), default=0)
    alt_text = models.CharField(_("accessibility alt text"), max_length=255, blank=True)
    tags = models.CharField(_("tags (comma separated)"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Media Asset")
        verbose_name_plural = _("Media Assets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_media_type_display()}] {self.title}"

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, "size"):
            try:
                self.file_size_bytes = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def file_extension(self) -> str:
        if self.file and "." in self.file.name:
            return self.file.name.split(".")[-1].upper()
        return ""


class PhotoGallery(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Photo gallery album for events, services, and outreach.
    """
    title = models.CharField(_("album title"), max_length=200)
    event_date = models.DateField(_("event date"), blank=True, null=True)
    description = models.TextField(_("album description"), blank=True)
    cover_image = models.ImageField(
        _("album cover photo"),
        upload_to=gallery_photo_upload_path,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Photo Gallery")
        verbose_name_plural = _("Photo Galleries")
        ordering = ["-event_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)


class GalleryImage(TimeStampedModel):
    """
    Individual photo inside a PhotoGallery.
    """
    gallery = models.ForeignKey(PhotoGallery, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("photo"), upload_to=gallery_photo_upload_path, validators=[validate_image_file])
    caption = models.CharField(_("caption"), max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("Gallery Image")
        verbose_name_plural = _("Gallery Images")
        ordering = ["sort_order", "created_at"]
