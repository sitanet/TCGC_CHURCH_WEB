"""
URL configuration for the public-facing church website.
"""
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    # Core Landing & Information
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("leadership/", views.LeadershipView.as_view(), name="leadership"),
    path("visit/", views.PlanVisitView.as_view(), name="visit"),
    path("plan-a-visit/", views.PlanVisitView.as_view(), name="plan_visit"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("prayer-request/", views.PrayerRequestView.as_view(), name="prayer_request"),
    path("newsletter/subscribe/", views.NewsletterSubscribeView.as_view(), name="newsletter_subscribe"),

    # Teachings & Sermons
    path("teachings/", views.TeachingsListView.as_view(), name="teachings_list"),
    path("teachings/<slug:slug>/", views.TeachingDetailView.as_view(), name="teaching_detail"),
    path("teachings/<slug:slug>/download-audio/", views.TeachingDownloadAudioView.as_view(), name="teaching_download_audio"),

    # Events & Conferences
    path("events/", views.EventsListView.as_view(), name="events_list"),
    path("events/<slug:slug>/", views.EventDetailView.as_view(), name="event_detail"),
    path("events/<slug:slug>/register/", views.EventRegisterView.as_view(), name="event_register"),
    path("conferences/", views.ConferencesListView.as_view(), name="conferences_list"),
    path("conferences/<slug:slug>/", views.ConferenceDetailView.as_view(), name="conference_detail"),

    # Ministries Directory
    path("ministries/", views.MinistriesListView.as_view(), name="ministries_list"),
    path("ministries/<slug:slug>/", views.MinistryDetailView.as_view(), name="ministry_detail"),

    # Publications & Journals
    path("publications/", views.PublicationsPublicListView.as_view(), name="publications_list"),
    path("publications/<slug:slug>/", views.PublicationPublicDetailView.as_view(), name="publication_detail"),
    path("publications/<slug:slug>/download/", views.PublicationDownloadView.as_view(), name="publication_download"),

    # Articles & Blog
    path("articles/", views.ArticlesListView.as_view(), name="articles_list"),
    path("articles/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),

    # Media Hub & Live Broadcast
    path("media/", views.MediaHubView.as_view(), name="media_hub"),
    path("media/photos/<slug:slug>/", views.PhotoGalleryDetailView.as_view(), name="gallery_detail"),
    path("live/", views.LiveStreamView.as_view(), name="live_stream"),

    # Search & Discovery
    path("search/", views.GlobalSearchView.as_view(), name="search"),
    path("sitemap.xml", views.SitemapView.as_view(), name="sitemap"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots"),
]
