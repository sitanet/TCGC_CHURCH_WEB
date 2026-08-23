"""
Comprehensive Administrative CMS Views for The CityGate Church Platform.
"""
import csv
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator

from django.contrib.auth import get_user_model
from apps.accounts.permissions import StaffRequiredMixin, RoleRequiredMixin
from apps.accounts.models import UserRole

User = get_user_model()
from apps.core.models import SiteConfiguration, HomepageConfig, ActivityLog, log_activity, PublishableStatus
from apps.teachings.models import Sermon, SermonSeries, SermonCategory, SermonScripture
from apps.articles.models import Article, ArticleCategory
from apps.announcements.models import Announcement
from apps.publications.models import Publication, PublicationCategory, PublicationType
from apps.people.models import Person, LeadershipCategory
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.events.models import Event, EventCategory, EventRegistration
from apps.conferences.models import Conference, ConferenceSpeaker, ConferenceSession
from apps.media_library.models import MediaAsset, PhotoGallery, GalleryImage, MediaType
from apps.streaming.models import LiveStreamChannel, StreamStatus
from apps.website.models import ContactMessage, ContactMessageStatus, PrayerRequest, PrayerRequestStatus, NewsletterSubscriber

from .forms import (
    TeachingForm, SermonSeriesForm, SermonScriptureForm,
    ArticleForm, AnnouncementForm, PublicationForm,
    PersonForm, MinistryForm, ChurchMeetingForm, ChurchLocationForm,
    EventForm, ConferenceForm, MediaAssetForm, PhotoGalleryForm,
    LiveStreamControlForm, HomepageConfigForm, SiteConfigurationForm,
    StaffUserCreateForm, StaffUserEditForm,
)


# ==============================================================================
# 1. DASHBOARD OVERVIEW & KPIS
# ==============================================================================

class DashboardIndexView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()

        # Real Database KPI Metrics
        total_teachings = Sermon.objects.count()
        total_audio = Sermon.objects.filter(audio_file__isnull=False).exclude(audio_file="").count() + MediaAsset.objects.filter(media_type=MediaType.AUDIO).count()
        total_videos = Sermon.objects.filter(Q(video_file__isnull=False) | Q(video_url__gt="") | Q(video_embed_code__gt="")).count() + MediaAsset.objects.filter(media_type=MediaType.VIDEO).count()
        total_articles = Article.objects.count()
        upcoming_events = Event.objects.filter(start_datetime__gte=now).count()
        total_conferences = Conference.objects.count()
        total_ministries = Ministry.objects.count()
        total_publications = Publication.objects.count()
        total_media_assets = MediaAsset.objects.count()
        total_downloads = Publication.objects.aggregate(Sum("download_count"))["download_count__sum"] or 0

        context["metrics"] = {
            "total_teachings": total_teachings,
            "total_audio": total_audio,
            "total_videos": total_videos,
            "total_articles": total_articles,
            "upcoming_events": upcoming_events,
            "total_conferences": total_conferences,
            "total_ministries": total_ministries,
            "total_publications": total_publications,
            "total_media": total_media_assets,
            "total_downloads": total_downloads,
        }

        # Activity timeline & Live stream status
        context["recent_activities"] = ActivityLog.objects.select_related("user").all()[:8]
        context["upcoming_events_list"] = Event.objects.filter(start_datetime__gte=now).order_by("start_datetime")[:4]
        context["live_channel"] = LiveStreamChannel.load()
        context["recent_teachings"] = Sermon.objects.select_related("speaker", "series").order_by("-created_at")[:4]
        return context


# ==============================================================================
# 2. TEACHINGS / SERMONS MANAGEMENT
# ==============================================================================

class TeachingListView(StaffRequiredMixin, ListView):
    model = Sermon
    template_name = "dashboard/teachings/list.html"
    context_object_name = "sermons"
    paginate_by = 12

    def get_queryset(self):
        qs = Sermon.objects.select_related("series", "category", "speaker").prefetch_related("scriptures").all()
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category")
        series = self.request.GET.get("series")
        speaker = self.request.GET.get("speaker")
        status = self.request.GET.get("status")
        featured = self.request.GET.get("featured")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(speaker_name__icontains=q) | Q(scripture_reference__icontains=q))
        if category:
            qs = qs.filter(category_id=category)
        if series:
            qs = qs.filter(series_id=series)
        if speaker:
            qs = qs.filter(speaker_id=speaker)
        if status:
            qs = qs.filter(status=status)
        if featured == "1":
            qs = qs.filter(is_featured=True)

        return qs.order_by("-preached_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = SermonCategory.objects.all()
        context["series_list"] = SermonSeries.objects.all()
        context["speakers"] = Person.objects.all()
        context["status_choices"] = PublishableStatus.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_series"] = self.request.GET.get("series", "")
        context["current_speaker"] = self.request.GET.get("speaker", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_featured"] = self.request.GET.get("featured", "")
        return context


class TeachingCreateView(StaffRequiredMixin, CreateView):
    model = Sermon
    form_class = TeachingForm
    template_name = "dashboard/teachings/form.html"
    success_url = reverse_lazy("dashboard:teachings_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Create New Teaching / Sermon"
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Process Scripture references from dynamic POST arrays
        self._save_scriptures(self.object)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created teaching record", self.request)
        messages.success(self.request, f"Teaching '{self.object.title}' has been successfully created.")
        return response

    def _save_scriptures(self, sermon):
        books = self.request.POST.getlist("scripture_book[]")
        chapters = self.request.POST.getlist("scripture_chapter[]")
        v_starts = self.request.POST.getlist("scripture_verse_start[]")
        v_ends = self.request.POST.getlist("scripture_verse_end[]")
        texts = self.request.POST.getlist("scripture_text[]")

        sermon.scriptures.all().delete()
        for idx in range(len(books)):
            b = books[idx].strip()
            if b and idx < len(chapters) and chapters[idx]:
                try:
                    c = int(chapters[idx])
                    vs = int(v_starts[idx]) if idx < len(v_starts) and v_starts[idx] else 1
                    ve = int(v_ends[idx]) if idx < len(v_ends) and v_ends[idx] else None
                    t = texts[idx] if idx < len(texts) else ""
                    SermonScripture.objects.create(
                        sermon=sermon,
                        book=b,
                        chapter=c,
                        verse_start=vs,
                        verse_end=ve,
                        scripture_text=t,
                        sort_order=idx,
                    )
                except (ValueError, TypeError):
                    pass


class TeachingEditView(StaffRequiredMixin, UpdateView):
    model = Sermon
    form_class = TeachingForm
    template_name = "dashboard/teachings/form.html"
    success_url = reverse_lazy("dashboard:teachings_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Edit Teaching: {self.object.title}"
        context["is_edit"] = True
        context["existing_scriptures"] = self.object.scriptures.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Update Scripture references
        TeachingCreateView._save_scriptures(self, self.object)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated teaching record", self.request)
        messages.success(self.request, f"Teaching '{self.object.title}' updated successfully.")
        return response


class TeachingDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        sermon = get_object_or_404(Sermon, pk=pk)
        title = sermon.title
        log_activity(request.user, ActivityLog.Action.DELETED, sermon, f"Deleted teaching: {title}", request)
        sermon.delete()
        messages.success(request, f"Teaching '{title}' deleted.")
        return redirect("dashboard:teachings_list")


class TeachingQuickActionView(StaffRequiredMixin, View):
    """
    Handles fast actions: publish, unpublish, duplicate, archive.
    """
    def post(self, request, pk, action):
        sermon = get_object_or_404(Sermon, pk=pk)
        if action == "publish":
            sermon.status = PublishableStatus.PUBLISHED
            sermon.published_at = datetime.now()
            sermon.save(update_fields=["status", "published_at"])
            log_activity(request.user, ActivityLog.Action.PUBLISHED, sermon, "Published teaching", request)
            messages.success(request, f"Teaching '{sermon.title}' is now PUBLISHED.")
        elif action == "unpublish":
            sermon.status = PublishableStatus.DRAFT
            sermon.save(update_fields=["status"])
            log_activity(request.user, ActivityLog.Action.UNPUBLISHED, sermon, "Unpublished teaching to draft", request)
            messages.info(request, f"Teaching '{sermon.title}' reverted to DRAFT.")
        elif action == "archive":
            sermon.status = PublishableStatus.ARCHIVED
            sermon.save(update_fields=["status"])
            log_activity(request.user, ActivityLog.Action.ARCHIVED, sermon, "Archived teaching", request)
            messages.info(request, f"Teaching '{sermon.title}' archived.")
        elif action == "duplicate":
            new_sermon = Sermon.objects.get(pk=pk)
            new_sermon.pk = None
            new_sermon.title = f"{sermon.title} (Copy)"
            new_sermon.slug = ""
            new_sermon.status = PublishableStatus.DRAFT
            new_sermon.save()
            log_activity(request.user, ActivityLog.Action.CREATED, new_sermon, f"Duplicated from '{sermon.title}'", request)
            messages.success(request, f"Teaching duplicated as '{new_sermon.title}'.")
            return redirect("dashboard:teaching_edit", pk=new_sermon.pk)

        return redirect("dashboard:teachings_list")


# Sermon Series
class SermonSeriesListView(StaffRequiredMixin, ListView):
    model = SermonSeries
    template_name = "dashboard/teachings/series_list.html"
    context_object_name = "series_list"
    paginate_by = 12

    def get_queryset(self):
        return SermonSeries.objects.annotate(sermon_count=Count("sermons")).order_by("-created_at")


class SermonSeriesCreateView(StaffRequiredMixin, CreateView):
    model = SermonSeries
    form_class = SermonSeriesForm
    template_name = "dashboard/teachings/series_form.html"
    success_url = reverse_lazy("dashboard:series_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created sermon series", self.request)
        messages.success(self.request, f"Series '{self.object.title}' created.")
        return response


class SermonSeriesEditView(StaffRequiredMixin, UpdateView):
    model = SermonSeries
    form_class = SermonSeriesForm
    template_name = "dashboard/teachings/series_form.html"
    success_url = reverse_lazy("dashboard:series_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated sermon series", self.request)
        messages.success(self.request, f"Series '{self.object.title}' updated.")
        return response


class SermonSeriesDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        series = get_object_or_404(SermonSeries, pk=pk)
        title = series.title
        series.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted sermon series: {title}", request, "SermonSeries", str(pk), title)
        messages.success(request, f"Series '{title}' deleted.")
        return redirect("dashboard:series_list")


# ==============================================================================
# 3. MEDIA MANAGEMENT (AUDIO, VIDEO, LIBRARY, PHOTO ALBUMS)
# ==============================================================================

class MediaLibraryView(StaffRequiredMixin, ListView):
    model = MediaAsset
    template_name = "dashboard/media/library.html"
    context_object_name = "assets"
    paginate_by = 24

    def get_queryset(self):
        qs = MediaAsset.objects.select_related("category").all()
        q = self.request.GET.get("q", "").strip()
        m_type = self.request.GET.get("type")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(tags__icontains=q))
        if m_type:
            qs = qs.filter(media_type=m_type)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["media_types"] = MediaType.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["view_mode"] = self.request.GET.get("view", "grid")
        context["upload_form"] = MediaAssetForm()
        return context

    def post(self, request, *args, **kwargs):
        form = MediaAssetForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save()
            log_activity(request.user, ActivityLog.Action.UPLOADED, asset, f"Uploaded media asset: {asset.title}", request)
            messages.success(request, f"Media asset '{asset.title}' uploaded successfully.")
        else:
            messages.error(request, "Failed to upload file. Please check file format and size limits.")
        return redirect("dashboard:media_library")


class AudioManagerView(StaffRequiredMixin, ListView):
    """
    Dedicated audio library view with inline player and sermon attachment.
    """
    model = Sermon
    template_name = "dashboard/media/audio.html"
    context_object_name = "audio_sermons"
    paginate_by = 15

    def get_queryset(self):
        qs = Sermon.objects.filter(audio_file__isnull=False).exclude(audio_file="").select_related("speaker", "series")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(speaker_name__icontains=q))
        return qs.order_by("-preached_date")


class VideoManagerView(StaffRequiredMixin, ListView):
    """
    Dedicated video library view with embed preview and streaming links.
    """
    model = Sermon
    template_name = "dashboard/media/video.html"
    context_object_name = "video_sermons"
    paginate_by = 12

    def get_queryset(self):
        qs = Sermon.objects.filter(Q(video_file__isnull=False) | Q(video_url__gt="") | Q(video_embed_code__gt="")).select_related("speaker", "series")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(speaker_name__icontains=q))
        return qs.order_by("-preached_date")


class MediaAssetDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(MediaAsset, pk=pk)
        title = asset.title
        asset.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted media asset: {title}", request, "MediaAsset", str(pk), title)
        messages.success(request, f"Asset '{title}' removed.")
        return redirect("dashboard:media_library")


# Photo Albums
class PhotoGalleryListView(StaffRequiredMixin, ListView):
    model = PhotoGallery
    template_name = "dashboard/media/albums_list.html"
    context_object_name = "albums"
    paginate_by = 12

    def get_queryset(self):
        return PhotoGallery.objects.annotate(photo_count=Count("images")).order_by("-event_date", "-created_at")


class PhotoGalleryCreateView(StaffRequiredMixin, CreateView):
    model = PhotoGallery
    form_class = PhotoGalleryForm
    template_name = "dashboard/media/album_form.html"
    success_url = reverse_lazy("dashboard:photo_albums_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self._handle_photos(self.object)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created photo album", self.request)
        messages.success(self.request, f"Album '{self.object.title}' created.")
        return response

    def _handle_photos(self, album):
        files = self.request.FILES.getlist("album_photos")
        for f in files:
            GalleryImage.objects.create(gallery=album, image=f)


class PhotoGalleryEditView(StaffRequiredMixin, UpdateView):
    model = PhotoGallery
    form_class = PhotoGalleryForm
    template_name = "dashboard/media/album_form.html"
    success_url = reverse_lazy("dashboard:photo_albums_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        PhotoGalleryCreateView._handle_photos(self, self.object)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated photo album", self.request)
        messages.success(self.request, f"Album '{self.object.title}' updated.")
        return response


class PhotoGalleryDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        album = get_object_or_404(PhotoGallery, pk=pk)
        title = album.title
        album.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted album: {title}", request, "PhotoGallery", str(pk), title)
        messages.success(request, f"Album '{title}' deleted.")
        return redirect("dashboard:photo_albums_list")


# ==============================================================================
# 4. ARTICLES & EDITORIAL
# ==============================================================================

class ArticleListView(StaffRequiredMixin, ListView):
    model = Article
    template_name = "dashboard/articles/list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        qs = Article.objects.select_related("category", "author").all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        category = self.request.GET.get("category")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by("-published_at", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ArticleCategory.objects.all()
        context["status_choices"] = PublishableStatus.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_category"] = self.request.GET.get("category", "")
        return context


class ArticleCreateView(StaffRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "dashboard/articles/form.html"
    success_url = reverse_lazy("dashboard:articles_list")

    def form_valid(self, form):
        if not form.instance.author:
            form.instance.author = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created article", self.request)
        messages.success(self.request, f"Article '{self.object.title}' created.")
        return response


class ArticleEditView(StaffRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "dashboard/articles/form.html"
    success_url = reverse_lazy("dashboard:articles_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated article", self.request)
        messages.success(self.request, f"Article '{self.object.title}' saved.")
        return response


class ArticleDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        title = article.title
        article.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted article: {title}", request, "Article", str(pk), title)
        messages.success(request, f"Article '{title}' deleted.")
        return redirect("dashboard:articles_list")


class ArticleToggleStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.status == PublishableStatus.PUBLISHED:
            article.status = PublishableStatus.DRAFT
            messages.info(request, f"Article '{article.title}' reverted to DRAFT.")
        else:
            article.status = PublishableStatus.PUBLISHED
            article.published_at = datetime.now()
            messages.success(request, f"Article '{article.title}' is now PUBLISHED.")
        article.save(update_fields=["status", "published_at"])
        return redirect("dashboard:articles_list")


# ==============================================================================
# 5. ANNOUNCEMENTS
# ==============================================================================

class AnnouncementListView(StaffRequiredMixin, ListView):
    model = Announcement
    template_name = "dashboard/announcements/list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        return Announcement.objects.order_by("-is_active", "-priority", "-created_at")


class AnnouncementCreateView(StaffRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "dashboard/announcements/form.html"
    success_url = reverse_lazy("dashboard:announcements_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created announcement", self.request)
        messages.success(self.request, f"Announcement '{self.object.title}' created.")
        return response


class AnnouncementEditView(StaffRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "dashboard/announcements/form.html"
    success_url = reverse_lazy("dashboard:announcements_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated announcement", self.request)
        messages.success(self.request, f"Announcement '{self.object.title}' updated.")
        return response


class AnnouncementDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        ann = get_object_or_404(Announcement, pk=pk)
        title = ann.title
        ann.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted announcement: {title}", request, "Announcement", str(pk), title)
        messages.success(request, f"Announcement '{title}' deleted.")
        return redirect("dashboard:announcements_list")


class AnnouncementToggleActiveView(StaffRequiredMixin, View):
    def post(self, request, pk):
        ann = get_object_or_404(Announcement, pk=pk)
        ann.is_active = not ann.is_active
        ann.save(update_fields=["is_active"])
        status_str = "ACTIVE" if ann.is_active else "INACTIVE"
        messages.success(request, f"Announcement '{ann.title}' marked as {status_str}.")
        return redirect("dashboard:announcements_list")


# ==============================================================================
# 6. PEOPLE & LEADERSHIP
# ==============================================================================

class PersonListView(StaffRequiredMixin, ListView):
    model = Person
    template_name = "dashboard/people/list.html"
    context_object_name = "people"
    paginate_by = 15

    def get_queryset(self):
        qs = Person.objects.select_related("category").all()
        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("category")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(title__icontains=q) | Q(biography__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        return qs.order_by("sort_order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = LeadershipCategory.objects.all()
        context["current_q"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        return context


class PersonCreateView(StaffRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "dashboard/people/form.html"
    success_url = reverse_lazy("dashboard:people_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, f"Added person: {self.object.name}", self.request)
        messages.success(self.request, f"Leader/Speaker '{self.object.name}' created.")
        return response


class PersonEditView(StaffRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "dashboard/people/form.html"
    success_url = reverse_lazy("dashboard:people_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, f"Updated person: {self.object.name}", self.request)
        messages.success(self.request, f"Person '{self.object.name}' updated.")
        return response


class PersonDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        name = person.name
        person.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted person: {name}", request, "Person", str(pk), name)
        messages.success(request, f"Person '{name}' removed.")
        return redirect("dashboard:people_list")


# ==============================================================================
# 7. MINISTRIES, MEETINGS & LOCATIONS
# ==============================================================================

class MinistryListView(StaffRequiredMixin, ListView):
    model = Ministry
    template_name = "dashboard/ministries/list.html"
    context_object_name = "ministries"

    def get_queryset(self):
        return Ministry.objects.select_related("leader").order_by("sort_order", "name")


class MinistryCreateView(StaffRequiredMixin, CreateView):
    model = Ministry
    form_class = MinistryForm
    template_name = "dashboard/ministries/form.html"
    success_url = reverse_lazy("dashboard:ministries_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created ministry", self.request)
        messages.success(self.request, f"Ministry '{self.object.name}' created.")
        return response


class MinistryEditView(StaffRequiredMixin, UpdateView):
    model = Ministry
    form_class = MinistryForm
    template_name = "dashboard/ministries/form.html"
    success_url = reverse_lazy("dashboard:ministries_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated ministry", self.request)
        messages.success(self.request, f"Ministry '{self.object.name}' updated.")
        return response


class MinistryDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        ministry = get_object_or_404(Ministry, pk=pk)
        name = ministry.name
        ministry.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted ministry: {name}", request, "Ministry", str(pk), name)
        messages.success(request, f"Ministry '{name}' deleted.")
        return redirect("dashboard:ministries_list")


# Recurring Meetings
class ChurchMeetingListView(StaffRequiredMixin, ListView):
    model = ChurchMeeting
    template_name = "dashboard/ministries/meetings_list.html"
    context_object_name = "meetings"

    def get_queryset(self):
        return ChurchMeeting.objects.select_related("ministry", "location").order_by("day_of_week", "start_time")


class ChurchMeetingCreateView(StaffRequiredMixin, CreateView):
    model = ChurchMeeting
    form_class = ChurchMeetingForm
    template_name = "dashboard/ministries/meeting_form.html"
    success_url = reverse_lazy("dashboard:meetings_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created recurring meeting", self.request)
        messages.success(self.request, f"Meeting '{self.object.name}' created.")
        return response


class ChurchMeetingEditView(StaffRequiredMixin, UpdateView):
    model = ChurchMeeting
    form_class = ChurchMeetingForm
    template_name = "dashboard/ministries/meeting_form.html"
    success_url = reverse_lazy("dashboard:meetings_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated recurring meeting", self.request)
        messages.success(self.request, f"Meeting '{self.object.name}' updated.")
        return response


class ChurchMeetingDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        meeting = get_object_or_404(ChurchMeeting, pk=pk)
        name = meeting.name
        meeting.delete()
        messages.success(request, f"Meeting '{name}' removed.")
        return redirect("dashboard:meetings_list")


# Locations
class ChurchLocationListView(StaffRequiredMixin, ListView):
    model = ChurchLocation
    template_name = "dashboard/ministries/locations_list.html"
    context_object_name = "locations"


class ChurchLocationCreateView(StaffRequiredMixin, CreateView):
    model = ChurchLocation
    form_class = ChurchLocationForm
    template_name = "dashboard/ministries/location_form.html"
    success_url = reverse_lazy("dashboard:locations_list")


class ChurchLocationEditView(StaffRequiredMixin, UpdateView):
    model = ChurchLocation
    form_class = ChurchLocationForm
    template_name = "dashboard/ministries/location_form.html"
    success_url = reverse_lazy("dashboard:locations_list")


class ChurchLocationDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        loc = get_object_or_404(ChurchLocation, pk=pk)
        name = loc.name
        loc.delete()
        messages.success(request, f"Location '{name}' removed.")
        return redirect("dashboard:locations_list")


# ==============================================================================
# 8. EVENTS & CONFERENCES
# ==============================================================================

class EventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "dashboard/events/list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        qs = Event.objects.select_related("category", "ministry", "speaker").all()
        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("category")
        status = self.request.GET.get("status")
        timeframe = self.request.GET.get("timeframe", "all")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(venue_name__icontains=q) | Q(description__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        if status:
            qs = qs.filter(status=status)
        if timeframe == "upcoming":
            qs = qs.filter(start_datetime__gte=datetime.now())
        elif timeframe == "past":
            qs = qs.filter(start_datetime__lt=datetime.now())

        return qs.order_by("-start_datetime")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = EventCategory.objects.all()
        context["current_q"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_timeframe"] = self.request.GET.get("timeframe", "all")
        context["view_mode"] = self.request.GET.get("view", "list")
        return context


class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/events/form.html"
    success_url = reverse_lazy("dashboard:events_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created event", self.request)
        messages.success(self.request, f"Event '{self.object.title}' created.")
        return response


class EventEditView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "dashboard/events/form.html"
    success_url = reverse_lazy("dashboard:events_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated event", self.request)
        messages.success(self.request, f"Event '{self.object.title}' updated.")
        return response


class EventDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        title = event.title
        event.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted event: {title}", request, "Event", str(pk), title)
        messages.success(request, f"Event '{title}' deleted.")
        return redirect("dashboard:events_list")


class EventRegistrationsListView(StaffRequiredMixin, ListView):
    model = EventRegistration
    template_name = "dashboard/events/registrations.html"
    context_object_name = "registrations"
    paginate_by = 25

    def get_queryset(self):
        qs = EventRegistration.objects.select_related("event").all()
        event_id = self.kwargs.get("event_id")
        if event_id:
            qs = qs.filter(event_id=event_id)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get("event_id")
        if event_id:
            context["event"] = get_object_or_404(Event, pk=event_id)
        return context


# Conferences
class ConferenceListView(StaffRequiredMixin, ListView):
    model = Conference
    template_name = "dashboard/conferences/list.html"
    context_object_name = "conferences"

    def get_queryset(self):
        return Conference.objects.annotate(speaker_count=Count("speakers"), session_count=Count("sessions")).order_by("-start_date")


class ConferenceCreateView(StaffRequiredMixin, CreateView):
    model = Conference
    form_class = ConferenceForm
    template_name = "dashboard/conferences/form.html"
    success_url = reverse_lazy("dashboard:conferences_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, "Created conference", self.request)
        messages.success(self.request, f"Conference '{self.object.title}' created.")
        return response


class ConferenceEditView(StaffRequiredMixin, UpdateView):
    model = Conference
    form_class = ConferenceForm
    template_name = "dashboard/conferences/form.html"
    success_url = reverse_lazy("dashboard:conferences_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, "Updated conference", self.request)
        messages.success(self.request, f"Conference '{self.object.title}' updated.")
        return response


class ConferenceDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        conf = get_object_or_404(Conference, pk=pk)
        title = conf.title
        conf.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted conference: {title}", request, "Conference", str(pk), title)
        messages.success(request, f"Conference '{title}' deleted.")
        return redirect("dashboard:conferences_list")


class ConferenceDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        conference = get_object_or_404(Conference.objects.prefetch_related("speakers__speaker", "sessions"), pk=pk)
        all_people = Person.objects.all()
        return render(request, "dashboard/conferences/detail.html", {
            "conference": conference,
            "all_people": all_people,
        })

    def post(self, request, pk):
        conference = get_object_or_404(Conference, pk=pk)
        action = request.POST.get("action")

        if action == "add_speaker":
            person_id = request.POST.get("person_id")
            name_override = request.POST.get("name_override", "")
            title_override = request.POST.get("title_override", "")
            person = Person.objects.filter(pk=person_id).first() if person_id else None
            ConferenceSpeaker.objects.create(
                conference=conference,
                speaker=person,
                name_override=name_override,
                title_override=title_override,
            )
            messages.success(request, "Speaker added to conference.")
        elif action == "add_session":
            title = request.POST.get("session_title")
            speaker_info = request.POST.get("speaker_info", "")
            s_date = request.POST.get("session_date")
            start = request.POST.get("start_time")
            end = request.POST.get("end_time") or None
            hall = request.POST.get("location_hall", "Main Auditorium")
            ConferenceSession.objects.create(
                conference=conference,
                session_title=title,
                speaker_info=speaker_info,
                session_date=s_date,
                start_time=start,
                end_time=end,
                location_hall=hall,
            )
            messages.success(request, "Session added to conference schedule.")

        return redirect("dashboard:conference_detail", pk=conference.pk)


# ==============================================================================
# 9. PUBLICATIONS & JOURNALS (HIGH PRIORITY)
# ==============================================================================

class PublicationListView(StaffRequiredMixin, ListView):
    model = Publication
    template_name = "dashboard/publications/list.html"
    context_object_name = "publications"
    paginate_by = 12

    def get_queryset(self):
        qs = Publication.objects.select_related("category").all()
        q = self.request.GET.get("q", "").strip()
        pub_type = self.request.GET.get("type")
        status = self.request.GET.get("status")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author_name__icontains=q) | Q(description__icontains=q) | Q(edition_volume__icontains=q))
        if pub_type:
            qs = qs.filter(publication_type=pub_type)
        if status:
            qs = qs.filter(status=status)

        return qs.order_by("-publication_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publication_types"] = PublicationType.choices
        context["status_choices"] = PublishableStatus.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


class PublicationCreateView(StaffRequiredMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = "dashboard/publications/form.html"
    success_url = reverse_lazy("dashboard:publications_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, f"Published {self.object.get_publication_type_display()}: {self.object.title}", self.request)
        messages.success(self.request, f"{self.object.get_publication_type_display()} '{self.object.title}' created successfully.")
        return response


class PublicationEditView(StaffRequiredMixin, UpdateView):
    model = Publication
    form_class = PublicationForm
    template_name = "dashboard/publications/form.html"
    success_url = reverse_lazy("dashboard:publications_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, f"Updated publication: {self.object.title}", self.request)
        messages.success(self.request, f"Publication '{self.object.title}' updated.")
        return response


class PublicationDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        pub = get_object_or_404(Publication, pk=pk)
        title = pub.title
        pub.delete()
        log_activity(request.user, ActivityLog.Action.DELETED, None, f"Deleted publication: {title}", request, "Publication", str(pk), title)
        messages.success(request, f"Publication '{title}' removed.")
        return redirect("dashboard:publications_list")


# ==============================================================================
# 10. LIVE STREAMING CONTROL CENTER
# ==============================================================================

class LiveStreamControlView(StaffRequiredMixin, View):
    template_name = "dashboard/streaming/control_center.html"

    def get(self, request):
        channel = LiveStreamChannel.load()
        form = LiveStreamControlForm(instance=channel)
        return render(request, self.template_name, {"channel": channel, "form": form})

    def post(self, request):
        channel = LiveStreamChannel.load()
        form = LiveStreamControlForm(request.POST, request.FILES, instance=channel)
        if form.is_valid():
            channel = form.save()
            log_activity(request.user, ActivityLog.Action.UPDATED, channel, f"Updated live stream status: {channel.get_stream_status_display()}", request)
            messages.success(request, f"Live stream broadcast settings updated. Current Status: {channel.get_stream_status_display()}")
            return redirect("dashboard:live_stream")
        return render(request, self.template_name, {"channel": channel, "form": form})


# ==============================================================================
# 11. COMMUNICATION INBOXES (CONTACT, PRAYER REQUESTS, NEWSLETTER)
# ==============================================================================

class ContactMessagesListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = "dashboard/communications/contact_messages.html"
    context_object_name = "contact_messages"
    paginate_by = 20

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(message__icontains=q) | Q(subject__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = ContactMessageStatus.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


class ContactMessageDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        if msg.status == ContactMessageStatus.NEW:
            msg.status = ContactMessageStatus.READ
            msg.save(update_fields=["status"])
        return render(request, "dashboard/communications/message_detail.html", {"msg": msg})

    def post(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        action = request.POST.get("action")
        if action == "mark_replied":
            msg.status = ContactMessageStatus.REPLIED
            msg.replied_at = datetime.now()
            msg.admin_notes = request.POST.get("admin_notes", "")
            msg.save()
            messages.success(request, "Message marked as replied.")
        elif action == "archive":
            msg.status = ContactMessageStatus.ARCHIVED
            msg.save(update_fields=["status"])
            messages.info(request, "Message archived.")
        return redirect("dashboard:contact_messages")


class PrayerRequestsListView(StaffRequiredMixin, ListView):
    model = PrayerRequest
    template_name = "dashboard/communications/prayer_requests.html"
    context_object_name = "prayers"
    paginate_by = 20

    def get_queryset(self):
        qs = PrayerRequest.objects.select_related("handled_by").all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(prayer_point__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = PrayerRequestStatus.choices
        context["current_q"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context

    def post(self, request):
        prayer_id = request.POST.get("prayer_id")
        action = request.POST.get("action")
        prayer = get_object_or_404(PrayerRequest, pk=prayer_id)
        if action == "mark_handled":
            prayer.status = PrayerRequestStatus.HANDLED
            prayer.handled_by = request.user
            prayer.pastoral_notes = request.POST.get("pastoral_notes", "")
            prayer.save()
            messages.success(request, f"Prayer request for {prayer.full_name} marked as Handled.")
        elif action == "mark_in_prayer":
            prayer.status = PrayerRequestStatus.IN_PRAYER
            prayer.handled_by = request.user
            prayer.save()
            messages.info(request, f"Prayer request for {prayer.full_name} moved to Intercession.")
        return redirect("dashboard:prayer_requests")


class NewsletterSubscribersListView(StaffRequiredMixin, ListView):
    model = NewsletterSubscriber
    template_name = "dashboard/communications/subscribers.html"
    context_object_name = "subscribers"
    paginate_by = 30

    def get_queryset(self):
        qs = NewsletterSubscriber.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(email__icontains=q) | Q(full_name__icontains=q))
        return qs.order_by("-subscribed_at")


class NewsletterExportCsvView(StaffRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="citygate_subscribers_{datetime.now():%Y%m%d}.csv"'
        writer = csv.writer(response)
        writer.writerow(["Email", "Full Name", "Active", "Subscribed At"])
        for sub in NewsletterSubscriber.objects.all():
            writer.writerow([sub.email, sub.full_name, "Yes" if sub.is_active else "No", sub.subscribed_at.strftime("%Y-%m-%d %H:%M")])
        return response


# ==============================================================================
# 12. ANALYTICS & TELEMETRY
# ==============================================================================

class AnalyticsOverviewView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/analytics/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.analytics.models import PageHit, MediaPlayEvent, DownloadEvent
        context["total_page_hits"] = PageHit.objects.count()
        context["recent_page_hits"] = PageHit.objects.all()[:10]
        context["top_teachings"] = Sermon.objects.order_by("-play_count")[:6]
        context["top_publications"] = Publication.objects.order_by("-download_count")[:6]
        context["recent_plays"] = MediaPlayEvent.objects.all()[:8]
        context["recent_downloads"] = DownloadEvent.objects.all()[:8]
        return context


# ==============================================================================
# 13. SYSTEM (USERS, AUDIT LOGS, SETTINGS)
# ==============================================================================

class StaffUserListView(RoleRequiredMixin, ListView):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    model = User
    template_name = "dashboard/system/users_list.html"
    context_object_name = "staff_users"

    def get_queryset(self):
        return User.objects.exclude(role=UserRole.MEMBER).order_by("-date_joined")


class StaffUserCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    model = User
    form_class = StaffUserCreateForm
    template_name = "dashboard/system/user_form.html"
    success_url = reverse_lazy("dashboard:users_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.CREATED, self.object, f"Created staff user: {self.object.username}", self.request)
        messages.success(self.request, f"Staff user '{self.object.username}' created.")
        return response


class StaffUserEditView(RoleRequiredMixin, UpdateView):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    model = User
    form_class = StaffUserEditForm
    template_name = "dashboard/system/user_form.html"
    success_url = reverse_lazy("dashboard:users_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, ActivityLog.Action.UPDATED, self.object, f"Updated staff user: {self.object.username}", self.request)
        messages.success(self.request, f"Staff user '{self.object.username}' updated.")
        return response


class StaffUserToggleActiveView(RoleRequiredMixin, View):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]

    def post(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)
        if user_obj == request.user:
            messages.error(request, "You cannot disable your own active account.")
            return redirect("dashboard:users_list")
        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=["is_active"])
        status_str = "ENABLED" if user_obj.is_active else "DISABLED"
        log_activity(request.user, ActivityLog.Action.STATUS_CHANGE, user_obj, f"Account {status_str}", request)
        messages.success(request, f"User '{user_obj.username}' is now {status_str}.")
        return redirect("dashboard:users_list")


class ActivityLogListView(RoleRequiredMixin, ListView):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    model = ActivityLog
    template_name = "dashboard/system/activity_logs.html"
    context_object_name = "logs"
    paginate_by = 30

    def get_queryset(self):
        qs = ActivityLog.objects.select_related("user").all()
        q = self.request.GET.get("q", "").strip()
        action = self.request.GET.get("action")
        if q:
            qs = qs.filter(Q(object_repr__icontains=q) | Q(details__icontains=q) | Q(user__username__icontains=q))
        if action:
            qs = qs.filter(action=action)
        return qs.order_by("-timestamp")


class HomepageSettingsView(RoleRequiredMixin, View):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.CONTENT_MANAGER]
    template_name = "dashboard/system/homepage_settings.html"

    def get(self, request):
        config = HomepageConfig.load()
        form = HomepageConfigForm(instance=config)
        return render(request, self.template_name, {"form": form, "config": config})

    def post(self, request):
        config = HomepageConfig.load()
        form = HomepageConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            log_activity(request.user, ActivityLog.Action.UPDATED, config, "Updated homepage hero and showcase settings", request)
            messages.success(request, "Homepage configuration saved successfully.")
            return redirect("dashboard:homepage_settings")
        return render(request, self.template_name, {"form": form, "config": config})


class WebsiteSettingsView(RoleRequiredMixin, View):
    allowed_roles = [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    template_name = "dashboard/system/website_settings.html"

    def get(self, request):
        config = SiteConfiguration.load()
        form = SiteConfigurationForm(instance=config)
        return render(request, self.template_name, {"form": form, "config": config})

    def post(self, request):
        config = SiteConfiguration.load()
        form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            log_activity(request.user, ActivityLog.Action.UPDATED, config, "Updated website global settings and branding", request)
            messages.success(request, "Website global settings updated successfully.")
            return redirect("dashboard:website_settings")
        return render(request, self.template_name, {"form": form, "config": config})
