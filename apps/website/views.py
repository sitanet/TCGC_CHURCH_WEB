"""
Public website views for The CityGate Church with dynamic content and submission handling.
"""
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import F

from apps.core.models import SiteConfiguration, HomepageConfig, PublishableStatus
from apps.teachings.models import Sermon, SermonSeries
from apps.events.models import Event
from apps.conferences.models import Conference
from apps.publications.models import Publication, PublicationType
from apps.articles.models import Article
from apps.people.models import Person
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.announcements.models import Announcement
from apps.website.models import ContactMessage, PrayerRequest, NewsletterSubscriber
from apps.analytics.models import DownloadEvent


class HomeView(TemplateView):
    """
    Dynamic public landing page view driven by HomepageConfig and database records.
    """
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_config = HomepageConfig.load()
        now = datetime.now()

        # Dynamic featured items (fallback to latest published if not set)
        featured_sermon = home_config.featured_teaching or Sermon.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-preached_date").first()
        featured_event = home_config.featured_event or Event.objects.filter(status=PublishableStatus.PUBLISHED, start_datetime__gte=now).order_by("start_datetime").first()
        featured_conf = home_config.featured_conference or Conference.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-start_date").first()
        featured_pub = home_config.featured_publication or Publication.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-publication_date", "-created_at").first()
        featured_art = home_config.featured_article or Article.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-published_at").first()

        context["hero"] = home_config
        context["featured_sermon"] = featured_sermon
        context["featured_event"] = featured_event
        context["featured_conference"] = featured_conf
        context["featured_publication"] = featured_pub
        context["featured_article"] = featured_art

        # Recent stream of published content
        context["recent_sermons"] = Sermon.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-preached_date")[:3]
        context["upcoming_events"] = Event.objects.filter(status=PublishableStatus.PUBLISHED, start_datetime__gte=now).order_by("start_datetime")[:3]
        context["recent_publications"] = Publication.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-created_at")[:4]
        context["recent_articles"] = Article.objects.filter(status=PublishableStatus.PUBLISHED).order_by("-published_at")[:3]
        context["active_announcements"] = Announcement.objects.filter(is_active=True, show_homepage=True).order_by("-priority", "-created_at")[:3]
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pastoral_team"] = Person.objects.filter(status=PublishableStatus.PUBLISHED, is_featured=True).order_by("sort_order")
        return context


class VisitView(TemplateView):
    template_name = "website/visit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meetings"] = ChurchMeeting.objects.filter(is_active=True).order_by("day_of_week", "start_time")
        context["campuses"] = ChurchLocation.objects.all().order_by("sort_order")
        return context


class ContactView(View):
    template_name = "website/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form_type = request.POST.get("form_type", "contact")

        if form_type == "prayer":
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
                )
                messages.success(request, "Your prayer request has been received confidentially by our pastoral prayer team. We stand in faith with you!")
            else:
                messages.error(request, "Please enter your name and prayer request.")
        else:
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
                messages.success(request, "Thank you for reaching out! Your message has been received and our pastoral team will connect with you shortly.")
            else:
                messages.error(request, "Please fill in all required contact fields.")

        return redirect("website:contact")


class NewsletterSubscribeView(View):
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
            messages.success(request, "Thank you for subscribing to The CityGate Church devotionals & updates!")
        else:
            messages.error(request, "Please provide a valid email address.")

        return redirect(request.META.get("HTTP_REFERER", "website:home"))


# ==============================================================================
# PUBLIC PUBLICATIONS & JOURNALS
# ==============================================================================

class PublicationsPublicListView(ListView):
    model = Publication
    template_name = "website/publications/list.html"
    context_object_name = "publications"
    paginate_by = 12

    def get_queryset(self):
        qs = Publication.objects.filter(status=PublishableStatus.PUBLISHED)
        pub_type = self.request.GET.get("type")
        if pub_type:
            qs = qs.filter(publication_type=pub_type)
        return qs.order_by("-publication_date", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["publication_types"] = PublicationType.choices
        context["current_type"] = self.request.GET.get("type", "")
        return context


class PublicationPublicDetailView(DetailView):
    model = Publication
    template_name = "website/publications/detail.html"
    context_object_name = "publication"

    def get_queryset(self):
        return Publication.objects.filter(status=PublishableStatus.PUBLISHED)


class PublicationDownloadView(View):
    """
    Secure download endpoint that tracks download telemetry before streaming the file.
    """
    def get(self, request, slug):
        pub = get_object_or_404(Publication, slug=slug, status=PublishableStatus.PUBLISHED)
        if not pub.pdf_file or not pub.is_downloadable:
            raise Http404("Document is not available for download.")

        # Increment download counter atomically
        Publication.objects.filter(pk=pub.pk).update(download_count=F("download_count") + 1)

        # Log analytics download event
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
