"""
URL configuration for custom CMS dashboard.
"""
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # 1. Overview
    path("", views.DashboardIndexView.as_view(), name="index"),

    # 2. Teachings & Sermons
    path("teachings/", views.TeachingListView.as_view(), name="teachings_list"),
    path("teachings/create/", views.TeachingCreateView.as_view(), name="teaching_create"),
    path("teachings/<int:pk>/edit/", views.TeachingEditView.as_view(), name="teaching_edit"),
    path("teachings/<int:pk>/delete/", views.TeachingDeleteView.as_view(), name="teaching_delete"),
    path("teachings/<int:pk>/action/<str:action>/", views.TeachingQuickActionView.as_view(), name="teaching_action"),
    path("teachings/series/", views.SermonSeriesListView.as_view(), name="series_list"),
    path("teachings/series/create/", views.SermonSeriesCreateView.as_view(), name="series_create"),
    path("teachings/series/<int:pk>/edit/", views.SermonSeriesEditView.as_view(), name="series_edit"),
    path("teachings/series/<int:pk>/delete/", views.SermonSeriesDeleteView.as_view(), name="series_delete"),

    # 3. Media & Photo Albums
    path("media/", views.MediaLibraryView.as_view(), name="media_library"),
    path("media/audio/", views.AudioManagerView.as_view(), name="audio_manager"),
    path("media/video/", views.VideoManagerView.as_view(), name="video_manager"),
    path("media/<int:pk>/delete/", views.MediaAssetDeleteView.as_view(), name="media_delete"),
    path("media/albums/", views.PhotoGalleryListView.as_view(), name="photo_albums_list"),
    path("media/albums/create/", views.PhotoGalleryCreateView.as_view(), name="photo_album_create"),
    path("media/albums/<int:pk>/edit/", views.PhotoGalleryEditView.as_view(), name="photo_album_edit"),
    path("media/albums/<int:pk>/delete/", views.PhotoGalleryDeleteView.as_view(), name="photo_album_delete"),

    # 4. Articles & Blog
    path("articles/", views.ArticleListView.as_view(), name="articles_list"),
    path("articles/create/", views.ArticleCreateView.as_view(), name="article_create"),
    path("articles/<int:pk>/edit/", views.ArticleEditView.as_view(), name="article_edit"),
    path("articles/<int:pk>/delete/", views.ArticleDeleteView.as_view(), name="article_delete"),
    path("articles/<int:pk>/toggle-status/", views.ArticleToggleStatusView.as_view(), name="article_toggle_status"),

    # 5. Announcements & Alerts
    path("announcements/", views.AnnouncementListView.as_view(), name="announcements_list"),
    path("announcements/create/", views.AnnouncementCreateView.as_view(), name="announcement_create"),
    path("announcements/<int:pk>/edit/", views.AnnouncementEditView.as_view(), name="announcement_edit"),
    path("announcements/<int:pk>/delete/", views.AnnouncementDeleteView.as_view(), name="announcement_delete"),
    path("announcements/<int:pk>/toggle-active/", views.AnnouncementToggleActiveView.as_view(), name="announcement_toggle_active"),

    # 6. People & Leadership
    path("people/", views.PersonListView.as_view(), name="people_list"),
    path("people/create/", views.PersonCreateView.as_view(), name="person_create"),
    path("people/<int:pk>/edit/", views.PersonEditView.as_view(), name="person_edit"),
    path("people/<int:pk>/delete/", views.PersonDeleteView.as_view(), name="person_delete"),

    # 7. Ministries, Meetings & Locations
    path("ministries/", views.MinistryListView.as_view(), name="ministries_list"),
    path("ministries/create/", views.MinistryCreateView.as_view(), name="ministry_create"),
    path("ministries/<int:pk>/edit/", views.MinistryEditView.as_view(), name="ministry_edit"),
    path("ministries/<int:pk>/delete/", views.MinistryDeleteView.as_view(), name="ministry_delete"),
    path("ministries/meetings/", views.ChurchMeetingListView.as_view(), name="meetings_list"),
    path("ministries/meetings/create/", views.ChurchMeetingCreateView.as_view(), name="meeting_create"),
    path("ministries/meetings/<int:pk>/edit/", views.ChurchMeetingEditView.as_view(), name="meeting_edit"),
    path("ministries/meetings/<int:pk>/delete/", views.ChurchMeetingDeleteView.as_view(), name="meeting_delete"),
    path("ministries/locations/", views.ChurchLocationListView.as_view(), name="locations_list"),
    path("ministries/locations/create/", views.ChurchLocationCreateView.as_view(), name="location_create"),
    path("ministries/locations/<int:pk>/edit/", views.ChurchLocationEditView.as_view(), name="location_edit"),
    path("ministries/locations/<int:pk>/delete/", views.ChurchLocationDeleteView.as_view(), name="location_delete"),

    # 8. Events & Conferences
    path("events/", views.EventListView.as_view(), name="events_list"),
    path("events/create/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", views.EventEditView.as_view(), name="event_edit"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),
    path("events/<int:event_id>/registrations/", views.EventRegistrationsListView.as_view(), name="event_registrations"),
    path("conferences/", views.ConferenceListView.as_view(), name="conferences_list"),
    path("conferences/create/", views.ConferenceCreateView.as_view(), name="conference_create"),
    path("conferences/<int:pk>/edit/", views.ConferenceEditView.as_view(), name="conference_edit"),
    path("conferences/<int:pk>/delete/", views.ConferenceDeleteView.as_view(), name="conference_delete"),
    path("conferences/<int:pk>/manage/", views.ConferenceDetailView.as_view(), name="conference_detail"),

    # 9. Publications & Journals (High Priority)
    path("publications/", views.PublicationListView.as_view(), name="publications_list"),
    path("publications/create/", views.PublicationCreateView.as_view(), name="publication_create"),
    path("publications/<int:pk>/edit/", views.PublicationEditView.as_view(), name="publication_edit"),
    path("publications/<int:pk>/delete/", views.PublicationDeleteView.as_view(), name="publication_delete"),

    # 10. Live Streaming Control Center
    path("live-stream/", views.LiveStreamControlView.as_view(), name="live_stream"),

    # 11. Communication Inboxes
    path("communications/messages/", views.ContactMessagesListView.as_view(), name="contact_messages"),
    path("communications/messages/<int:pk>/", views.ContactMessageDetailView.as_view(), name="contact_message_detail"),
    path("communications/prayers/", views.PrayerRequestsListView.as_view(), name="prayer_requests"),
    path("communications/subscribers/", views.NewsletterSubscribersListView.as_view(), name="subscribers_list"),
    path("communications/subscribers/export/", views.NewsletterExportCsvView.as_view(), name="subscribers_export"),

    # 12. Analytics
    path("analytics/", views.AnalyticsOverviewView.as_view(), name="analytics_overview"),

    # 13. System Settings & Users
    path("system/users/", views.StaffUserListView.as_view(), name="users_list"),
    path("system/users/create/", views.StaffUserCreateView.as_view(), name="user_create"),
    path("system/users/<int:pk>/edit/", views.StaffUserEditView.as_view(), name="user_edit"),
    path("system/users/<int:pk>/toggle-active/", views.StaffUserToggleActiveView.as_view(), name="user_toggle_active"),
    path("system/activity-logs/", views.ActivityLogListView.as_view(), name="activity_logs"),
    path("system/homepage/", views.HomepageSettingsView.as_view(), name="homepage_settings"),
    path("system/settings/", views.WebsiteSettingsView.as_view(), name="website_settings"),
]
