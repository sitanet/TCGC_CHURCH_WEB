"""
Custom CMS Forms for The CityGate Church Dashboard.
Clean, styled, accessible inputs with server-side validation.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from apps.core.models import SiteConfiguration, HomepageConfig
from apps.teachings.models import Sermon, SermonSeries, SermonCategory, SermonScripture
from apps.articles.models import Article, ArticleCategory
from apps.announcements.models import Announcement
from apps.publications.models import Publication, PublicationCategory
from apps.people.models import Person, LeadershipCategory
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.events.models import Event, EventCategory
from apps.conferences.models import Conference, ConferenceSpeaker, ConferenceSession
from apps.media_library.models import MediaAsset, PhotoGallery, MediaCategory, MediaType
from apps.streaming.models import LiveStreamChannel
from apps.website.models import ContactMessage, PrayerRequest
from apps.core.validators import (
    validate_image_file, validate_document_file, validate_audio_file, validate_video_file
)

User = get_user_model()


# Base Styled Form Mixin
class StyledFormMixin:
    """
    Applies standard CityGate CMS CSS classes to form fields automatically.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "slug" in self.fields:
            self.fields["slug"].required = False
        if "sort_order" in self.fields:
            self.fields["sort_order"].required = False
        for name, field in self.fields.items():
            widget = field.widget
            widget_type = widget.__class__.__name__

            if widget_type in ("TextInput", "EmailInput", "URLInput", "NumberInput", "DateInput", "TimeInput", "DateTimeInput"):
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_class} form-input".strip()
            elif widget_type == "Textarea":
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_class} form-textarea".strip()
                if "rows" not in widget.attrs:
                    widget.attrs["rows"] = 4
            elif widget_type in ("Select", "SelectMultiple"):
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_class} form-select".strip()
            elif widget_type == "CheckboxInput":
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_class} form-checkbox".strip()
            elif widget_type in ("FileInput", "ClearableFileInput"):
                existing_class = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_class} form-file-input".strip()


# ==============================================================================
# TEACHINGS & SERMON FORMS
# ==============================================================================

class TeachingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Sermon
        fields = [
            "title",
            "slug",
            "series",
            "category",
            "speaker",
            "speaker_name",
            "preached_date",
            "summary",
            "study_notes",
            "scripture_reference",
            "tags",
            "cover_image",
            "audio_file",
            "video_file",
            "video_url",
            "video_embed_code",
            "transcript_text",
            "transcript_file",
            "status",
            "published_at",
            "scheduled_at",
            "is_featured",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "preached_date": forms.DateInput(attrs={"type": "date"}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "summary": forms.Textarea(attrs={"rows": 3, "placeholder": "Brief message summary for card previews"}),
            "study_notes": forms.Textarea(attrs={"rows": 6, "placeholder": "Key sermon outline points, notes, and principles"}),
            "transcript_text": forms.Textarea(attrs={"rows": 8, "placeholder": "Paste or edit full message transcript here..."}),
            "tags": forms.TextInput(attrs={"placeholder": "faith, grace, prayer, breakthrough"}),
        }

    def clean_cover_image(self):
        img = self.cleaned_data.get("cover_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img

    def clean_audio_file(self):
        aud = self.cleaned_data.get("audio_file")
        if aud and hasattr(aud, "size"):
            validate_audio_file(aud)
        return aud

    def clean_video_file(self):
        vid = self.cleaned_data.get("video_file")
        if vid and hasattr(vid, "size"):
            validate_video_file(vid)
        return vid

    def clean_transcript_file(self):
        doc = self.cleaned_data.get("transcript_file")
        if doc and hasattr(doc, "size"):
            validate_document_file(doc)
        return doc


class SermonSeriesForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SermonSeries
        fields = ["title", "slug", "description", "cover_image", "start_date", "end_date", "status", "is_featured"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class SermonScriptureForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SermonScripture
        fields = ["book", "chapter", "verse_start", "verse_end", "scripture_text", "sort_order"]
        widgets = {
            "book": forms.TextInput(attrs={"placeholder": "e.g. Romans"}),
            "scripture_text": forms.Textarea(attrs={"rows": 2, "placeholder": "Passage text..."}),
        }


# ==============================================================================
# ARTICLES & ANNOUNCEMENTS FORMS
# ==============================================================================

class ArticleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "category",
            "author",
            "author_name_override",
            "summary",
            "body",
            "featured_image",
            "tags",
            "status",
            "published_at",
            "scheduled_at",
            "is_featured",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "summary": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 12, "placeholder": "Compose article content..."}),
        }

    def clean_featured_image(self):
        img = self.cleaned_data.get("featured_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class AnnouncementForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "message",
            "image",
            "link_url",
            "link_label",
            "priority",
            "show_banner",
            "show_homepage",
            "is_active",
            "start_date",
            "expires_at",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_image(self):
        img = self.cleaned_data.get("image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


# ==============================================================================
# PUBLICATIONS & JOURNALS FORMS
# ==============================================================================

class PublicationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            "title",
            "slug",
            "publication_type",
            "edition_volume",
            "category",
            "author_name",
            "description",
            "publication_date",
            "cover_image",
            "pdf_file",
            "is_downloadable",
            "status",
            "is_featured",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date"}),
            "edition_volume": forms.TextInput(attrs={"placeholder": "e.g. Vol. 4 Issue 1, 2026 Edition"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Overview and synopsis of this publication..."}),
        }

    def clean_cover_image(self):
        img = self.cleaned_data.get("cover_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img

    def clean_pdf_file(self):
        doc = self.cleaned_data.get("pdf_file")
        if doc and hasattr(doc, "size"):
            validate_document_file(doc)
        return doc


# ==============================================================================
# PEOPLE & MINISTRIES FORMS
# ==============================================================================

class PersonForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "slug",
            "title",
            "category",
            "photo",
            "biography",
            "email",
            "phone",
            "twitter_handle",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "sort_order",
            "is_featured",
            "status",
        ]
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 5}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Senior Pastor, Minister of Music, Guest Speaker"}),
        }

    def clean_photo(self):
        img = self.cleaned_data.get("photo")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class MinistryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Ministry
        fields = [
            "name",
            "slug",
            "tagline",
            "description",
            "icon_name",
            "cover_image",
            "leader",
            "meeting_schedule",
            "meeting_location",
            "contact_email",
            "contact_phone",
            "accepts_volunteers",
            "sort_order",
            "is_featured",
            "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "icon_name": forms.TextInput(attrs={"placeholder": "heart, users, book-open, shield, music"}),
        }

    def clean_cover_image(self):
        img = self.cleaned_data.get("cover_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class ChurchMeetingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ChurchMeeting
        fields = [
            "name",
            "slug",
            "ministry",
            "location",
            "day_of_week",
            "start_time",
            "end_time",
            "location_hall",
            "is_online",
            "stream_link",
            "description",
            "is_active",
            "sort_order",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ChurchLocationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ChurchLocation
        fields = [
            "name",
            "slug",
            "address",
            "city",
            "state",
            "country",
            "is_main_campus",
            "phone",
            "email",
            "google_maps_url",
            "photo",
            "sort_order",
        ]

    def clean_photo(self):
        img = self.cleaned_data.get("photo")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


# ==============================================================================
# EVENTS & CONFERENCES FORMS
# ==============================================================================

class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "slug",
            "category",
            "ministry",
            "speaker",
            "speaker_name",
            "tagline",
            "description",
            "banner_image",
            "start_datetime",
            "end_datetime",
            "is_recurring",
            "recurrence_rule",
            "venue_name",
            "venue_address",
            "location",
            "is_online",
            "stream_link",
            "requires_registration",
            "registration_url",
            "max_attendees",
            "is_free",
            "contact_email",
            "contact_phone",
            "status",
            "is_featured",
        ]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_banner_image(self):
        img = self.cleaned_data.get("banner_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class ConferenceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Conference
        fields = [
            "title",
            "slug",
            "theme",
            "year",
            "description",
            "banner_image",
            "start_date",
            "end_date",
            "venue",
            "address",
            "registration_link",
            "schedule_document",
            "audio_stream_url",
            "video_stream_url",
            "status",
            "is_featured",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_banner_image(self):
        img = self.cleaned_data.get("banner_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img

    def clean_schedule_document(self):
        doc = self.cleaned_data.get("schedule_document")
        if doc and hasattr(doc, "size"):
            validate_document_file(doc)
        return doc


# ==============================================================================
# MEDIA LIBRARY FORMS
# ==============================================================================

class MediaAssetForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ["title", "media_type", "category", "file", "alt_text", "tags", "status"]

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if f and hasattr(f, "size"):
            mtype = self.cleaned_data.get("media_type")
            if mtype == MediaType.AUDIO:
                validate_audio_file(f)
            elif mtype == MediaType.VIDEO:
                validate_video_file(f)
            elif mtype == MediaType.DOCUMENT:
                validate_document_file(f)
            elif mtype == MediaType.IMAGE:
                validate_image_file(f)
        return f


class PhotoGalleryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PhotoGallery
        fields = ["title", "slug", "event_date", "description", "cover_image", "status", "is_featured"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_cover_image(self):
        img = self.cleaned_data.get("cover_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


# ==============================================================================
# LIVE STREAMING FORM
# ==============================================================================

class LiveStreamControlForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LiveStreamChannel
        fields = [
            "title",
            "platform",
            "stream_status",
            "stream_url",
            "audio_stream_url",
            "current_program",
            "current_topic",
            "current_speaker",
            "start_time",
            "end_time",
            "next_program",
            "next_broadcast_time",
            "offline_poster_image",
            "viewer_count",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "next_broadcast_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_offline_poster_image(self):
        img = self.cleaned_data.get("offline_poster_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


# ==============================================================================
# SYSTEM & HOMEPAGE SETTINGS FORMS
# ==============================================================================

class HomepageConfigForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = HomepageConfig
        fields = [
            "hero_tag",
            "hero_title",
            "hero_subtitle",
            "hero_image",
            "hero_video_url",
            "primary_cta_text",
            "primary_cta_link",
            "secondary_cta_text",
            "secondary_cta_link",
            "service_banner_title",
            "service_banner_desc",
            "service_banner_times",
            "featured_teaching",
            "featured_event",
            "featured_conference",
            "featured_publication",
            "featured_article",
        ]
        widgets = {
            "hero_subtitle": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_hero_image(self):
        img = self.cleaned_data.get("hero_image")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class SiteConfigurationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            "site_name",
            "tagline",
            "church_vision_short",
            "logo",
            "logo_dark",
            "favicon",
            "email",
            "phone_primary",
            "phone_secondary",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "google_maps_embed_url",
            "sunday_service_times",
            "midweek_service_times",
            "prayer_meeting_times",
            "youtube_url",
            "facebook_url",
            "instagram_url",
            "twitter_x_url",
            "telegram_url",
            "tiktok_url",
            "default_meta_title",
            "default_meta_description",
            "default_og_image",
            "giving_text",
            "footer_text",
            "copyright_override",
        ]
        widgets = {
            "church_vision_short": forms.Textarea(attrs={"rows": 3}),
            "giving_text": forms.Textarea(attrs={"rows": 4, "placeholder": "Bank account names, numbers, online giving instructions..."}),
            "footer_text": forms.Textarea(attrs={"rows": 3}),
            "default_meta_description": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_logo(self):
        img = self.cleaned_data.get("logo")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img

    def clean_favicon(self):
        img = self.cleaned_data.get("favicon")
        if img and hasattr(img, "size"):
            validate_image_file(img)
        return img


class StaffUserCreateForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Temporary staff password"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "title", "department", "phone_number", "is_active", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class StaffUserEditForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "title", "department", "phone_number", "is_active"]
