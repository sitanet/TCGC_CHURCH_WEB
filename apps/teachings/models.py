"""
Models for Teachings, Sermons, Categories, and Sermon Series.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel
from apps.core.storage import sermon_audio_upload_path, sermon_cover_upload_path
from apps.core.validators import validate_image_file, validate_audio_file, validate_video_file, validate_pdf_file


class SermonCategory(TimeStampedModel, SluggedModel):
    """
    Topic category for teachings (e.g. Faith, Grace, Kingdom Leadership, Prosperity, Family).
    """
    name = models.CharField(_("category name"), max_length=100)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("Sermon Category")
        verbose_name_plural = _("Sermon Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class SermonSeries(TimeStampedModel, SluggedModel, PublishableModel, SEOModel):
    """
    Thematic sermon series grouping individual messages.
    """
    title = models.CharField(_("series title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    cover_image = models.ImageField(
        _("cover art"),
        upload_to=sermon_cover_upload_path,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
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
    Individual sermon / teaching audio, video recording, and transcript.
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
    category = models.ForeignKey(
        SermonCategory,
        on_delete=models.SET_NULL,
        related_name="sermons",
        blank=True,
        null=True,
        verbose_name=_("topic category"),
    )
    speaker = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        related_name="sermons",
        blank=True,
        null=True,
        verbose_name=_("speaker / minister"),
    )
    speaker_name = models.CharField(_("speaker name override"), max_length=150, default="Pastor", blank=True)
    
    scripture_reference = models.CharField(_("primary scripture reference"), max_length=200, blank=True)
    preached_date = models.DateField(_("date preached"), db_index=True)
    summary = models.TextField(_("message summary / excerpt"), blank=True)
    study_notes = models.TextField(_("study notes / outline"), blank=True)
    transcript_text = models.TextField(_("full message transcript"), blank=True)
    transcript_file = models.FileField(
        _("transcript document / PDF"),
        upload_to="teachings/transcripts/",
        validators=[validate_pdf_file],
        blank=True,
        null=True,
    )
    tags = models.CharField(_("tags (comma separated)"), max_length=255, blank=True)
    
    # Media Files & Streaming
    cover_image = models.ImageField(
        _("cover image"),
        upload_to=sermon_cover_upload_path,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )
    cover_image_url = models.URLField(_("external cover image URL"), blank=True)
    audio_file = models.FileField(
        _("audio recording (MP3)"),
        upload_to=sermon_audio_upload_path,
        validators=[validate_audio_file],
        blank=True,
        null=True,
    )
    audio_url = models.URLField(_("external audio stream / download URL"), blank=True)
    video_file = models.FileField(
        _("uploaded video file (MP4)"),
        upload_to="teachings/videos/",
        validators=[validate_video_file],
        blank=True,
        null=True,
    )
    video_url = models.URLField(_("YouTube / Vimeo video URL"), blank=True)
    video_embed_code = models.TextField(_("custom embed code"), blank=True)
    audio_duration_seconds = models.PositiveIntegerField(_("audio duration (seconds)"), default=0)
    
    # Telemetry
    play_count = models.PositiveIntegerField(_("play count"), default=0)
    download_count = models.PositiveIntegerField(_("download count"), default=0)

    class Meta:
        verbose_name = _("Sermon / Teaching")
        verbose_name_plural = _("Sermons & Teachings")
        ordering = ["-preached_date", "-created_at"]

    def __str__(self):
        speaker = self.get_speaker_display()
        return f"{self.title} — {speaker}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def get_speaker_display(self) -> str:
        if self.speaker:
            return self.speaker.name
        return self.speaker_name or "Pastor"

    @property
    def audio_playback_url(self) -> str:
        if self.audio_file:
            try:
                return self.audio_file.url
            except Exception:
                pass
        return self.audio_url or ""

    @property
    def cover_image_display_url(self) -> str:
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                pass
        return self.cover_image_url or ""

    @property
    def has_audio(self) -> bool:
        return bool(self.audio_file or self.audio_url)

    @property
    def has_video(self) -> bool:
        return bool(self.video_file or self.video_url or self.video_embed_code)

    @property
    def has_transcript(self) -> bool:
        return bool(self.transcript_text or self.transcript_file)


class SermonScripture(OrderedModel):
    """
    Individual scripture passages cited in a teaching.
    """
    sermon = models.ForeignKey(Sermon, on_delete=models.CASCADE, related_name="scriptures")
    book = models.CharField(_("Bible Book"), max_length=50, help_text="e.g. Romans, Psalm, John")
    chapter = models.PositiveIntegerField(_("Chapter"))
    verse_start = models.PositiveIntegerField(_("Start Verse"))
    verse_end = models.PositiveIntegerField(_("End Verse"), blank=True, null=True)
    scripture_text = models.TextField(_("Scripture Quotation"), blank=True)

    class Meta:
        verbose_name = _("Sermon Scripture Reference")
        verbose_name_plural = _("Sermon Scripture References")
        ordering = ["sort_order", "id"]

    def __str__(self):
        verses = f"{self.verse_start}"
        if self.verse_end:
            verses += f"-{self.verse_end}"
        return f"{self.book} {self.chapter}:{verses}"
