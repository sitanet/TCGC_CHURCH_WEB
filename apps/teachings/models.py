"""
Models for Teachings, Sermons and Sermon Series.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel
from apps.core.storage import sermon_audio_upload_path, sermon_cover_upload_path


class SermonSeries(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Thematic sermon series grouping individual messages.
    """
    title = models.CharField(_("series title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    cover_image = models.ImageField(_("cover art"), upload_to=sermon_cover_upload_path, blank=True, null=True)
    start_date = models.DateField(_("start date"), blank=True, null=True)
    end_date = models.DateField(_("end date"), blank=True, null=True)

    class Meta:
        verbose_name = _("Sermon Series")
        verbose_name_plural = _("Sermon Series")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)


class Sermon(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Individual sermon / teaching audio & video recording.
    """
    title = models.CharField(_("sermon title"), max_length=255)
    series = models.ForeignKey(
        SermonSeries,
        on_delete=models.SET_NULL,
        related_name="sermons",
        blank=True,
        null=True,
        verbose_name=_("sermon series"),
    )
    speaker_name = models.CharField(_("speaker name"), max_length=150, default="Pastor")
    scripture_reference = models.CharField(_("scripture reference"), max_length=200, blank=True)
    preached_date = models.DateField(_("date preached"), db_index=True)
    summary = models.TextField(_("message summary"), blank=True)
    study_notes = models.TextField(_("study notes / outline"), blank=True)
    
    # Media Links & Files
    cover_image = models.ImageField(_("cover image"), upload_to=sermon_cover_upload_path, blank=True, null=True)
    audio_file = models.FileField(_("audio MP3 file"), upload_to=sermon_audio_upload_path, blank=True, null=True)
    video_url = models.URLField(_("YouTube / Vimeo video URL"), blank=True)
    audio_duration_seconds = models.PositiveIntegerField(_("audio duration (seconds)"), default=0)
    
    # Telemetry
    play_count = models.PositiveIntegerField(_("play count"), default=0)
    download_count = models.PositiveIntegerField(_("download count"), default=0)

    class Meta:
        verbose_name = _("Sermon / Teaching")
        verbose_name_plural = _("Sermons & Teachings")
        ordering = ["-preached_date", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.speaker_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)
