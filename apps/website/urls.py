"""
URL configuration for the public-facing church website.
"""
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("visit/", views.VisitView.as_view(), name="visit"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("newsletter/subscribe/", views.NewsletterSubscribeView.as_view(), name="newsletter_subscribe"),
    
    # Public Publications & Journals
    path("publications/", views.PublicationsPublicListView.as_view(), name="publications_list"),
    path("publications/<slug:slug>/", views.PublicationPublicDetailView.as_view(), name="publication_detail"),
    path("publications/<slug:slug>/download/", views.PublicationDownloadView.as_view(), name="publication_download"),
]
