"""
Public website views for The CityGate Church platform.
International-standard, fully database-driven, and accessible.
"""
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.urls import reverse

from apps.core.models import SiteConfiguration, HomepageConfig, PublishableStatus
from apps.teachings.models import Sermon, SermonSeries, SermonCategory, SermonScripture
from apps.events.models import Event, EventCategory, EventRegistration
from apps.conferences.models import Conference, ConferenceSpeaker, ConferenceSession
from apps.publications.models import Publication, PublicationCategory, PublicationType
from apps.articles.models import Article, ArticleCategory
from apps.people.models import Person, LeadershipCategory
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.announcements.models import Announcement
from apps.media_library.models import MediaAsset, PhotoGallery, MediaType
from apps.streaming.models import LiveStreamChannel, StreamStatus
from apps.website.models import ContactMessage, PrayerRequest, NewsletterSubscriber
from apps.analytics.models import DownloadEvent


# ==============================================================================
# 1. HOMEPAGE & CORE PAGES
# ==============================================================================

class HomeView(TemplateView):
    """
    Dynamic landing page driven by HomepageConfig and database records.
    Optimized with select_related and prefetch_related for maximum throughput.
    """
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_config = HomepageConfig.load()
        now = datetime.now()

        # Dynamic featured content with optimized joins
        featured_sermon = home_config.featured_teaching
        if not featured_sermon:
            featured_sermon = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).select_related("series", "speaker", "category").order_by("-preached_date").first()

        featured_event = home_config.featured_event
        if not featured_event:
            featured_event = Event.objects.filter(status=PublishableStatus.PUBLISHED, start_datetime__gte=now).select_related("category", "speaker").order_by("start_datetime").first()

        featured_conf = home_config.featured_conference
        if not featured_conf:
            featured_conf = Conference.objects.filter(status=PublishableStatus.PUBLISHED).prefetch_related("speakers").order_by("-start_date").first()

        featured_pub = home_config.featured_publication
        if not featured_pub:
            featured_pub = Publication.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-publication_date", "-created_at").first()

        featured_art = home_config.featured_article
        if not featured_art:
            featured_art = Article.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "author").order_by("-published_at").first()

        context["hero"] = home_config
        context["live_channel"] = LiveStreamChannel.load()
        context["featured_sermon"] = featured_sermon
        context["featured_event"] = featured_event
        context["featured_conference"] = featured_conf
        context["featured_publication"] = featured_pub
        context["featured_article"] = featured_art

        # Recent content streams with eager loading
        context["latest_sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).select_related("series", "speaker", "category").order_by("-preached_date")[:3]
        context["upcoming_events"] = Event.objects.filter(status=PublishableStatus.PUBLISHED, start_datetime__gte=now).select_related("category", "speaker", "ministry").order_by("start_datetime")[:3]
        context["showcase_ministries"] = Ministry.objects.filter(status=PublishableStatus.PUBLISHED).select_related("leader").order_by("sort_order")[:4]
        context["recent_publications"] = Publication.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-created_at")[:4]
        context["recent_articles"] = Article.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "author").order_by("-published_at")[:3]
        context["active_announcements"] = Announcement.objects.filter(is_active=True, show_homepage=True).order_by("-priority", "-created_at")[:3]
        return context


class AboutView(TemplateView):
    """
    About The CityGate Church: Vision, Mission, Beliefs, Spiritual Heritage & Leadership.
    """
    template_name = "website/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leadership_team"] = Person.objects.filter(status=PublishableStatus.PUBLISHED, is_featured=True).order_by("sort_order")[:6]
        return context


class LeadershipView(ListView):
    """
    Full leadership and pastoral directory.
    """
    model = Person
    template_name = "website/leadership.html"
    context_object_name = "leaders"

    def get_queryset(self):
        return Person.objects.filter(status=PublishableStatus.PUBLISHED).order_by("sort_order", "name")


class PlanVisitView(TemplateView):
    """
    Visitor guide: Service schedules, campus directions, what to expect, children church, and VIP pre-registration.
    """
    template_name = "website/visit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meetings"] = ChurchMeeting.objects.filter(is_active=True).select_related("location", "ministry").order_by("day_of_week", "start_time")
        context["campuses"] = ChurchLocation.objects.all().order_by("sort_order")
        return context


class ContactView(View):
    """
    Public Contact page with contact inquiry form handler.
    """
    template_name = "website/contact.html"

    def get(self, request):
        campuses = ChurchLocation.objects.all().order_by("sort_order")
        return render(request, self.template_name, {"campuses": campuses})

    def post(self, request):
        form_type = request.POST.get("form_type", "contact")

        if form_type == "prayer" or "prayer_point" in request.POST:
            name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()
            prayer_point = request.POST.get("prayer_point", "").strip()

            if name and prayer_point:
                PrayerRequest.objects.create(
                    full_name=name,
                    email=email,
                    phone=phone,
                    prayer_point=prayer_point,
                    is_confidential=True,
                )
                messages.success(request, "Your prayer request has been received with total confidentiality. Our pastoral intercession team is standing in faith with you!")
            else:
                messages.error(request, "Please provide your name and your prayer request.")
            return redirect("website:contact")

        name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "General Inquiry").strip()
        msg_text = request.POST.get("message", "").strip()

        if name and email and msg_text:
            ContactMessage.objects.create(
                full_name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=msg_text,
            )
            messages.success(request, "Thank you for contacting The CityGate Church! Our team will reach out to you shortly.")
        else:
            messages.error(request, "Please fill in all required fields.")

        return redirect("website:contact")


class PrayerRequestView(View):
    """
    Dedicated, confidential pastoral prayer portal.
    """
    template_name = "website/prayer_request.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        prayer_point = request.POST.get("prayer_point", "").strip()

        if name and prayer_point:
            PrayerRequest.objects.create(
                full_name=name,
                email=email,
                phone=phone,
                prayer_point=prayer_point,
                is_confidential=True,
            )
            messages.success(request, "Your prayer request has been received with total confidentiality. Our pastoral intercession team is standing in faith with you!")
        else:
            messages.error(request, "Please provide your name and your prayer request.")

        return redirect("website:prayer_request")


class NewsletterSubscribeView(View):
    """
    Public newsletter & devotional subscription handler.
    """
    def post(self, request):
        email = request.POST.get("email", "").strip().lower()
        full_name = request.POST.get("full_name", "").strip()

        if email:
            sub, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if not created and not sub.is_active:
                sub.is_active = True
                sub.save(update_fields=["is_active"])
            if full_name and not sub.full_name:
                sub.full_name = full_name
                sub.save(update_fields=["full_name"])
            messages.success(request, "Thank you for subscribing to The CityGate Church updates & devotionals!")
        else:
            messages.error(request, "Please provide a valid email address.")

        return redirect(request.META.get("HTTP_REFERER", "website:home"))


# ==============================================================================
# 2. TEACHINGS & SERMONS
# ==============================================================================

class TeachingsListView(ListView):
    """
    Public teaching library with search and multi-filtering.
    """
    model = Sermon
    template_name = "website/teachings/list.html"
    context_object_name = "sermons"
    paginate_by = 12

    def get_queryset(self):
        qs = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).select_related("series", "speaker", "category")
        q = self.request.GET.get("q")
        series_slug = self.request.GET.get("series")
        category_slug = self.request.GET.get("category")
        speaker_id = self.request.GET.get("speaker")
        media_filter = self.request.GET.get("media")

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(summary__icontains=q) |
                Q(speaker_name__icontains=q) |
                Q(speaker__name__icontains=q) |
                Q(scripture_reference__icontains=q)
            )
        if series_slug:
            qs = qs.filter(series__slug=series_slug)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if speaker_id:
            qs = qs.filter(speaker_id=speaker_id)
        if media_filter == "audio":
            qs = qs.exclude(audio_file="")
        elif media_filter == "video":
            qs = qs.filter(Q(video_file__isnull=False) | ~Q(video_url=""))

        return qs.order_by("-preached_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = SermonCategory.objects.all()
        context["series_list"] = SermonSeries.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-start_date")
        context["speakers"] = Person.objects.filter(status=PublishableStatus.PUBLISHED).order_by("name")
        context["featured_sermon"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED, is_featured=True).order_by("-preached_date").first()
        context["current_q"] = self.request.GET.get("q", "")
        context["current_series"] = self.request.GET.get("series", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_speaker"] = self.request.GET.get("speaker", "")
        context["current_media"] = self.request.GET.get("media", "")
        return context


class TeachingDetailView(DetailView):
    """
    World-class teaching detail experience with HTML5 audio player, video embed, transcript reader, and scripture references.
    """
    model = Sermon
    template_name = "website/teachings/detail.html"
    context_object_name = "sermon"

    def get_queryset(self):
        return Sermon.objects.filter(status=PublishableStatus.PUBLISHED).select_related("series", "speaker", "category").prefetch_related("scriptures")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment play telemetry atomically
        Sermon.objects.filter(pk=self.object.pk).update(play_count=F("play_count") + 1)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sermon = self.object
        # Related sermons from same series or speaker
        related = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).exclude(pk=sermon.pk)
        if sermon.series:
            related = related.filter(series=sermon.series)
        elif sermon.speaker:
            related = related.filter(speaker=sermon.speaker)
        context["related_sermons"] = related.order_by("-preached_date")[:3]
        return context


class TeachingDownloadAudioView(View):
    """
    Audio download tracking endpoint.
    """
    def get(self, request, slug):
        sermon = get_object_or_404(Sermon, slug=slug, status=PublishableStatus.PUBLISHED)
        if not sermon.audio_file:
            raise Http404("Audio file not available.")
        
        Sermon.objects.filter(pk=sermon.pk).update(download_count=F("download_count") + 1)
        return FileResponse(sermon.audio_file.open("rb"), as_attachment=True, filename=f"{sermon.slug}.mp3")


# ==============================================================================
# 3. EVENTS & CONFERENCES
# ==============================================================================

class EventsListView(ListView):
    """
    Church events & calendar cards with timeframe and category filters.
    """
    model = Event
    template_name = "website/events/list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        qs = Event.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "ministry", "speaker")
        timeframe = self.request.GET.get("timeframe", "upcoming")
        category_id = self.request.GET.get("category")
        now = datetime.now()

        if timeframe == "upcoming":
            qs = qs.filter(start_datetime__gte=now).order_by("start_datetime")
        elif timeframe == "past":
            qs = qs.filter(start_datetime__lt=now).order_by("-start_datetime")
        else:
            qs = qs.order_by("start_datetime")

        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        context["categories"] = EventCategory.objects.all()
        context["featured_event"] = Event.objects.filter(status=PublishableStatus.PUBLISHED, is_featured=True, start_datetime__gte=now).order_by("start_datetime").first()
        context["current_timeframe"] = self.request.GET.get("timeframe", "upcoming")
        context["current_category"] = self.request.GET.get("category", "")
        return context


class EventDetailView(DetailView):
    """
    Event details with venue, speaker, map, and attendee registration form.
    """
    model = Event
    template_name = "website/events/detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "ministry", "speaker", "location")


class EventRegisterView(View):
    """
    Public event attendee registration endpoint.
    """
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, status=PublishableStatus.PUBLISHED)
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        notes = request.POST.get("notes", "").strip()

        if full_name and email:
            if event.max_attendees and event.registrations.count() >= event.max_attendees:
                messages.error(request, "Registration for this event has reached maximum capacity.")
            else:
                EventRegistration.objects.create(
                    event=event,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    notes=notes,
                    is_confirmed=True,
                )
                messages.success(request, f"Registration confirmed for {event.title}! A confirmation email will be sent to {email}.")
        else:
            messages.error(request, "Please enter your name and email address to register.")

        return redirect("website:event_detail", slug=slug)


class ConferencesListView(ListView):
    model = Conference
    template_name = "website/conferences/list.html"
    context_object_name = "conferences"

    def get_queryset(self):
        return Conference.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-year", "-start_date")


class ConferenceDetailView(DetailView):
    model = Conference
    template_name = "website/conferences/detail.html"
    context_object_name = "conference"

    def get_queryset(self):
        return Conference.objects.filter(status=PublishableStatus.PUBLISHED).prefetch_related("speakers", "sessions")


# ==============================================================================
# 4. MINISTRIES
# ==============================================================================

class MinistriesListView(ListView):
    """
    Complete ministries directory.
    """
    model = Ministry
    template_name = "website/ministries/list.html"
    context_object_name = "ministries"

    def get_queryset(self):
        return Ministry.objects.filter(status=PublishableStatus.PUBLISHED).select_related("leader").prefetch_related("meetings").order_by("sort_order")


class MinistryDetailView(DetailView):
    model = Ministry
    template_name = "website/ministries/detail.html"
    context_object_name = "ministry"

    def get_queryset(self):
        return Ministry.objects.filter(status=PublishableStatus.PUBLISHED).select_related("leader").prefetch_related("meetings")


# ==============================================================================
# 5. PUBLICATIONS & JOURNALS
# ==============================================================================

class PublicationsPublicListView(ListView):
    model = Publication
    template_name = "website/publications/list.html"
    context_object_name = "publications"
    paginate_by = 12

    def get_queryset(self):
        qs = Publication.objects.filter(status=PublishableStatus.PUBLISHED)
        pub_type = self.request.GET.get("type")
        q = self.request.GET.get("q")
        if pub_type:
            qs = qs.filter(publication_type=pub_type)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(author_name__icontains=q))
        return qs.order_by("-publication_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publication_types"] = PublicationType.choices
        context["current_type"] = self.request.GET.get("type", "")
        context["current_q"] = self.request.GET.get("q", "")
        return context


class PublicationPublicDetailView(DetailView):
    model = Publication
    template_name = "website/publications/detail.html"
    context_object_name = "publication"

    def get_queryset(self):
        return Publication.objects.filter(status=PublishableStatus.PUBLISHED)


class PublicationDownloadView(View):
    """
    Download endpoint tracking download telemetry before streaming.
    """
    def get(self, request, slug):
        pub = get_object_or_404(Publication, slug=slug, status=PublishableStatus.PUBLISHED)
        if not pub.pdf_file or not pub.is_downloadable:
            raise Http404("Document is not available for download.")

        Publication.objects.filter(pk=pub.pk).update(download_count=F("download_count") + 1)
        try:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
            DownloadEvent.objects.create(
                resource_type="publication",
                resource_id=pub.pk,
                resource_title=pub.title,
                ip_address=ip.split(",")[0] if ip else None,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            )
        except Exception:
            pass

        return FileResponse(pub.pdf_file.open("rb"), as_attachment=True, filename=f"{pub.slug}.pdf")


# ==============================================================================
# 6. ARTICLES & BLOG
# ==============================================================================

class ArticlesListView(ListView):
    model = Article
    template_name = "website/articles/list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        qs = Article.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "author")
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs.order_by("-published_at", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ArticleCategory.objects.all()
        context["featured_article"] = Article.objects.filter(status=PublishableStatus.PUBLISHED, is_featured=True).order_by("-published_at").first()
        context["current_category"] = self.request.GET.get("category", "")
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "website/articles/detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.filter(status=PublishableStatus.PUBLISHED).select_related("category", "author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_articles"] = Article.objects.filter(status=PublishableStatus.PUBLISHED).exclude(pk=self.object.pk).order_by("-published_at")[:3]
        return context


# ==============================================================================
# 7. MEDIA HUB, PHOTO GALLERIES & LIVE BROADCAST
# ==============================================================================

class MediaHubView(TemplateView):
    """
    Unified Media Library: Audio Teachings, Video archives, Photo Albums, Downloadable Resources.
    """
    template_name = "website/media/hub.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["audio_sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).exclude(audio_file="").order_by("-preached_date")[:6]
        context["video_sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).filter(Q(video_file__isnull=False) | ~Q(video_url="")).order_by("-preached_date")[:6]
        context["photo_galleries"] = PhotoGallery.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-event_date")[:6]
        context["featured_publications"] = Publication.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-publication_date")[:4]
        return context


class PhotoGalleryDetailView(DetailView):
    model = PhotoGallery
    template_name = "website/media/gallery_detail.html"
    context_object_name = "gallery"

    def get_queryset(self):
        return PhotoGallery.objects.filter(status=PublishableStatus.PUBLISHED).prefetch_related("images")


class LiveStreamView(TemplateView):
    """
    Dedicated Live Broadcasting Room with video/audio streams, topic, preacher, and prayer link.
    """
    template_name = "website/live.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["channel"] = LiveStreamChannel.load()
        context["recent_sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-preached_date")[:4]
        return context


# ==============================================================================
# 8. GLOBAL SEARCH, SITEMAP & ROBOTS
# ==============================================================================

class GlobalSearchView(TemplateView):
    """
    Fast multi-model search across Sermons, Articles, Events, Publications, Ministries, and People.
    """
    template_name = "website/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        context["q"] = q

        if q:
            context["sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(title__icontains=q) | Q(summary__icontains=q) | Q(speaker_name__icontains=q) | Q(scripture_reference__icontains=q)
            )[:8]
            context["articles"] = Article.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q)
            )[:8]
            context["events"] = Event.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(venue_name__icontains=q)
            )[:6]
            context["conferences"] = Conference.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(title__icontains=q) | Q(theme__icontains=q) | Q(description__icontains=q)
            )[:6]
            context["publications"] = Publication.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(author_name__icontains=q)
            )[:6]
            context["ministries"] = Ministry.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(tagline__icontains=q)
            )[:6]
            context["people"] = Person.objects.filter(status=PublishableStatus.PUBLISHED).filter(
                Q(name__icontains=q) | Q(title__icontains=q) | Q(biography__icontains=q)
            )[:6]
            context["total_results"] = (
                len(context["sermons"]) + len(context["articles"]) + len(context["events"]) +
                len(context["conferences"]) + len(context["publications"]) +
                len(context["ministries"]) + len(context["people"])
            )
        else:
            context["total_results"] = 0

        return context


class SitemapView(View):
    """
    Dynamic XML sitemap for SEO discovery.
    """
    def get(self, request):
        domain = request.build_absolute_uri("/").rstrip("/")
        urls = [
            {"loc": f"{domain}/", "priority": "1.0", "changefreq": "daily"},
            {"loc": f"{domain}/about/", "priority": "0.8", "changefreq": "monthly"},
            {"loc": f"{domain}/leadership/", "priority": "0.8", "changefreq": "monthly"},
            {"loc": f"{domain}/visit/", "priority": "0.9", "changefreq": "monthly"},
            {"loc": f"{domain}/plan-a-visit/", "priority": "0.9", "changefreq": "monthly"},
            {"loc": f"{domain}/contact/", "priority": "0.8", "changefreq": "monthly"},
            {"loc": f"{domain}/prayer-request/", "priority": "0.8", "changefreq": "monthly"},
            {"loc": f"{domain}/teachings/", "priority": "0.9", "changefreq": "weekly"},
            {"loc": f"{domain}/events/", "priority": "0.9", "changefreq": "weekly"},
            {"loc": f"{domain}/ministries/", "priority": "0.8", "changefreq": "monthly"},
            {"loc": f"{domain}/publications/", "priority": "0.9", "changefreq": "weekly"},
            {"loc": f"{domain}/articles/", "priority": "0.8", "changefreq": "weekly"},
            {"loc": f"{domain}/media/", "priority": "0.8", "changefreq": "weekly"},
            {"loc": f"{domain}/live/", "priority": "0.9", "changefreq": "daily"},
        ]

        for s in Sermon.objects.filter(status=PublishableStatus.PUBLISHED).values("slug", "updated_at"):
            urls.append({"loc": f"{domain}/teachings/{s['slug']}/", "priority": "0.8", "changefreq": "monthly"})
        for e in Event.objects.filter(status=PublishableStatus.PUBLISHED).values("slug", "updated_at"):
            urls.append({"loc": f"{domain}/events/{e['slug']}/", "priority": "0.8", "changefreq": "weekly"})
        for p in Publication.objects.filter(status=PublishableStatus.PUBLISHED).values("slug", "updated_at"):
            urls.append({"loc": f"{domain}/publications/{p['slug']}/", "priority": "0.8", "changefreq": "monthly"})
        for a in Article.objects.filter(status=PublishableStatus.PUBLISHED).values("slug", "updated_at"):
            urls.append({"loc": f"{domain}/articles/{a['slug']}/", "priority": "0.7", "changefreq": "monthly"})

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            xml += f'  <url>\n    <loc>{u["loc"]}</loc>\n    <changefreq>{u["changefreq"]}</changefreq>\n    <priority>{u["priority"]}</priority>\n  </url>\n'
        xml += '</urlset>'

        return HttpResponse(xml, content_type="application/xml")


class RobotsTxtView(View):
    def get(self, request):
        domain = request.build_absolute_uri("/").rstrip("/")
        content = f"User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /django-admin/\nDisallow: /api/\n\nSitemap: {domain}/sitemap.xml\n"
        return HttpResponse(content, content_type="text/plain")
