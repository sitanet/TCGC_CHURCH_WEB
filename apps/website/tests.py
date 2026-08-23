"""
Comprehensive Test Suite for The CityGate Church Public Website.
"""
from datetime import datetime, date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.accounts.models import UserRole
from apps.core.models import SiteConfiguration, HomepageConfig, PublishableStatus
from apps.teachings.models import Sermon, SermonSeries, SermonCategory, SermonScripture
from apps.publications.models import Publication, PublicationCategory, PublicationType
from apps.people.models import Person
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.events.models import Event, EventCategory, EventRegistration
from apps.conferences.models import Conference, ConferenceSpeaker, ConferenceSession
from apps.articles.models import Article, ArticleCategory
from apps.announcements.models import Announcement
from apps.media_library.models import MediaAsset, PhotoGallery, GalleryImage
from apps.streaming.models import LiveStreamChannel, StreamStatus
from apps.website.models import ContactMessage, PrayerRequest, NewsletterSubscriber

User = get_user_model()


class CityGatePublicWebsiteTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Pastor & Speaker
        self.pastor = Person.objects.create(
            name="Pastor Samuel Adebayo",
            title="Senior Pastor",
            biography="Senior pastor of The CityGate Church with a divine apostolic commission.",
            status=PublishableStatus.PUBLISHED,
            is_featured=True,
        )

        # Sermon Series & Category & Sermon
        self.series = SermonSeries.objects.create(
            title="Apostolic Foundations",
            description="Deep dive into the apostolic blueprint of the New Testament church.",
            status=PublishableStatus.PUBLISHED,
        )
        self.category = SermonCategory.objects.create(
            name="Faith & Spiritual Authority",
            description="Teachings on kingdom faith and victory.",
        )
        self.dummy_audio = SimpleUploadedFile("sermon_audio.mp3", b"dummy mp3 audio stream", content_type="audio/mpeg")
        self.sermon = Sermon.objects.create(
            title="Walking in Divine Dominion",
            speaker=self.pastor,
            series=self.series,
            category=self.category,
            preached_date=date.today(),
            summary="A transformative revelation on kingdom dominion and authority.",
            scripture_reference="Ephesians 1:19-23",
            audio_file=self.dummy_audio,
            transcript_text="Welcome to today's message on Divine Dominion...",
            status=PublishableStatus.PUBLISHED,
            is_featured=True,
        )
        SermonScripture.objects.create(
            sermon=self.sermon,
            book="Ephesians",
            chapter=1,
            verse_start=19,
            verse_end=23,
            scripture_text="And what is the exceeding greatness of his power toward us who believe...",
        )

        # Ministry, Meeting, Campus
        self.campus = ChurchLocation.objects.create(
            name="Main Island Auditorium",
            address="10 Kingdom Way, Lekki Phase 1",
            city="Lagos",
            country="Nigeria",
            is_main_campus=True,
        )
        self.ministry = Ministry.objects.create(
            name="CityGate Worship & Arts",
            tagline="An Atmosphere of Pure Worship",
            description="Ministers of sound and praise leading the congregation into God's presence.",
            leader=self.pastor,
            meeting_schedule="Thursdays at 6:00 PM",
            status=PublishableStatus.PUBLISHED,
        )
        self.meeting = ChurchMeeting.objects.create(
            name="Sunday Divine Encounter Service",
            ministry=self.ministry,
            location=self.campus,
            day_of_week=0, # Sunday
            start_time="08:00",
            end_time="10:00",
            location_hall="Main Auditorium",
            is_active=True,
        )

        # Event
        self.event_cat = EventCategory.objects.create(name="Revival Conventions")
        self.event = Event.objects.create(
            title="Annual Believers Holy Ghost Convention",
            category=self.event_cat,
            speaker=self.pastor,
            ministry=self.ministry,
            start_datetime=datetime.now() + timedelta(days=10),
            end_datetime=datetime.now() + timedelta(days=10, hours=3),
            venue_name="Main Campus Auditorium",
            venue_address="10 Kingdom Way, Lekki",
            requires_registration=True,
            max_attendees=500,
            status=PublishableStatus.PUBLISHED,
            is_featured=True,
        )

        # Conference
        self.conference = Conference.objects.create(
            title="International Apostolic Leadership Summit",
            theme="Dimensions of Kingdom Dominion",
            year=2026,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=33),
            venue="CityGate Dome",
            status=PublishableStatus.PUBLISHED,
        )

        # Publication / Journal
        self.dummy_pdf = SimpleUploadedFile("journal_edition.pdf", b"%PDF-1.4 dummy pdf document", content_type="application/pdf")
        self.publication = Publication.objects.create(
            title="The Apostolic Herald Journal",
            publication_type=PublicationType.JOURNAL,
            edition_volume="Vol. 5 Issue 1 (2026)",
            author_name="Pastoral Theological Council",
            description="Theological treatise on apostolic leadership in the contemporary world.",
            pdf_file=self.dummy_pdf,
            is_downloadable=True,
            status=PublishableStatus.PUBLISHED,
            is_featured=True,
        )

        # Article
        self.art_cat = ArticleCategory.objects.create(name="Spiritual Growth")
        self.article = Article.objects.create(
            title="The Mystery of Kingdom Prayer and Fasting",
            category=self.art_cat,
            summary="Understanding the spiritual mechanics of answered prayers.",
            body="When believers engage in biblical fasting and prayer, heaven responds with divine clarity...",
            reading_time_minutes=4,
            status=PublishableStatus.PUBLISHED,
            is_featured=True,
        )

        # Photo Gallery
        self.gallery = PhotoGallery.objects.create(
            title="Sunday Divine Encounter Moments",
            event_date=date.today(),
            status=PublishableStatus.PUBLISHED,
        )

    # =========================================================================
    # 1. CORE PUBLIC ROUTES (200 OK)
    # =========================================================================

    def test_homepage_renders_cleanly(self):
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Walking in Divine Dominion")
        self.assertContains(response, "Annual Believers Holy Ghost Convention")
        self.assertContains(response, "The Apostolic Herald Journal")

    def test_about_page(self):
        response = self.client.get(reverse("website:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What We Believe")
        self.assertContains(response, "Pastor Samuel Adebayo")

    def test_leadership_directory_page(self):
        response = self.client.get(reverse("website:leadership"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pastor Samuel Adebayo")
        self.assertContains(response, "Senior Pastor")

    def test_plan_a_visit_page(self):
        response = self.client.get(reverse("website:plan_visit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sunday Divine Encounter Service")
        self.assertContains(response, "Main Island Auditorium")

    def test_contact_page_get(self):
        response = self.client.get(reverse("website:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connect Directly")

    def test_prayer_request_page_get(self):
        response = self.client.get(reverse("website:prayer_request"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "How Can We Stand in Faith With You?")

    # =========================================================================
    # 2. TEACHINGS & SERMONS WORKFLOW
    # =========================================================================

    def test_teachings_list_page(self):
        response = self.client.get(reverse("website:teachings_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Walking in Divine Dominion")

    def test_teachings_list_filter(self):
        response = self.client.get(reverse("website:teachings_list") + f"?series={self.series.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Walking in Divine Dominion")

    def test_teaching_detail_page_and_play_telemetry(self):
        initial_plays = self.sermon.play_count
        response = self.client.get(reverse("website:teaching_detail", kwargs={"slug": self.sermon.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Walking in Divine Dominion")
        self.assertContains(response, "Ephesians 1:19-23")
        self.assertContains(response, "Audio Broadcast")

        self.sermon.refresh_from_db()
        self.assertEqual(self.sermon.play_count, initial_plays + 1)

    def test_teaching_audio_download_telemetry(self):
        initial_dl = self.sermon.download_count
        response = self.client.get(reverse("website:teaching_download_audio", kwargs={"slug": self.sermon.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "audio/mpeg")

        self.sermon.refresh_from_db()
        self.assertEqual(self.sermon.download_count, initial_dl + 1)

    # =========================================================================
    # 3. EVENTS & CONFERENCES WORKFLOW
    # =========================================================================

    def test_events_list_page(self):
        response = self.client.get(reverse("website:events_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annual Believers Holy Ghost Convention")

    def test_event_detail_page(self):
        response = self.client.get(reverse("website:event_detail", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annual Believers Holy Ghost Convention")
        self.assertContains(response, "Register for this Event")

    def test_event_attendee_registration(self):
        post_data = {
            "full_name": "Brother Emmanuel Johnson",
            "email": "emmanuel@example.com",
            "phone": "+2348033334444",
            "notes": "Attending with family",
        }
        response = self.client.post(reverse("website:event_register", kwargs={"slug": self.event.slug}), post_data)
        self.assertEqual(response.status_code, 302)

        reg = EventRegistration.objects.filter(event=self.event, email="emmanuel@example.com").first()
        self.assertIsNotNone(reg)
        self.assertEqual(reg.full_name, "Brother Emmanuel Johnson")

    def test_conferences_list_and_detail(self):
        res_list = self.client.get(reverse("website:conferences_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "International Apostolic Leadership Summit")

        res_detail = self.client.get(reverse("website:conference_detail", kwargs={"slug": self.conference.slug}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Dimensions of Kingdom Dominion")

    # =========================================================================
    # 4. MINISTRIES WORKFLOW
    # =========================================================================

    def test_ministries_list_and_detail(self):
        res_list = self.client.get(reverse("website:ministries_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "CityGate Worship &amp; Arts")

        res_detail = self.client.get(reverse("website:ministry_detail", kwargs={"slug": self.ministry.slug}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "An Atmosphere of Pure Worship")

    # =========================================================================
    # 5. PUBLICATIONS / JOURNALS WORKFLOW
    # =========================================================================

    def test_publications_list_detail_and_telemetry_download(self):
        res_list = self.client.get(reverse("website:publications_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "The Apostolic Herald Journal")

        res_detail = self.client.get(reverse("website:publication_detail", kwargs={"slug": self.publication.slug}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Pastoral Theological Council")

        # Download PDF with telemetry
        initial_dl = self.publication.download_count
        res_dl = self.client.get(reverse("website:publication_download", kwargs={"slug": self.publication.slug}))
        self.assertEqual(res_dl.status_code, 200)
        self.assertEqual(res_dl["Content-Type"], "application/pdf")

        self.publication.refresh_from_db()
        self.assertEqual(self.publication.download_count, initial_dl + 1)

    # =========================================================================
    # 6. ARTICLES / BLOG WORKFLOW
    # =========================================================================

    def test_articles_list_and_detail(self):
        res_list = self.client.get(reverse("website:articles_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "The Mystery of Kingdom Prayer and Fasting")

        res_detail = self.client.get(reverse("website:article_detail", kwargs={"slug": self.article.slug}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "min read")

    # =========================================================================
    # 7. MEDIA HUB & LIVE STREAM ROOM
    # =========================================================================

    def test_media_hub_page(self):
        response = self.client.get(reverse("website:media_hub"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Media Center &amp; Archives")

    def test_photo_gallery_detail(self):
        response = self.client.get(reverse("website:gallery_detail", kwargs={"slug": self.gallery.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sunday Divine Encounter Moments")

    def test_live_stream_page(self):
        response = self.client.get(reverse("website:live_stream"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Broadcast is Currently Offline")

    # =========================================================================
    # 8. SEARCH, SITEMAP & FORMS
    # =========================================================================

    def test_global_search_queries(self):
        response = self.client.get(reverse("website:search") + "?q=dominion")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Walking in Divine Dominion")
        self.assertContains(response, "International Apostolic Leadership Summit")

    def test_contact_form_submission(self):
        data = {
            "full_name": "Sister Deborah",
            "email": "deborah@example.com",
            "phone": "+2348000000000",
            "subject": "Choir Auditions",
            "message": "I would like to know when choir rehearsals hold.",
        }
        response = self.client.post(reverse("website:contact"), data)
        self.assertEqual(response.status_code, 302)

        msg = ContactMessage.objects.filter(email="deborah@example.com").first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.full_name, "Sister Deborah")

    def test_prayer_request_submission(self):
        data = {
            "full_name": "Brother David",
            "email": "david@example.com",
            "prayer_point": "Please pray for divine wisdom and favor in my career.",
        }
        response = self.client.post(reverse("website:prayer_request"), data)
        self.assertEqual(response.status_code, 302)

        req = PrayerRequest.objects.filter(full_name="Brother David").first()
        self.assertIsNotNone(req)
        self.assertTrue(req.is_confidential)

    def test_sitemap_xml(self):
        response = self.client.get(reverse("website:sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertIn(b"<urlset", response.content)
        self.assertIn(b"/teachings/", response.content)

    def test_robots_txt(self):
        response = self.client.get(reverse("website:robots"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"User-agent: *", response.content)
