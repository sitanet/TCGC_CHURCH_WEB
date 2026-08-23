"""
Comprehensive Test Suite for CityGate Admin Dashboard & Content Management System.
"""
from datetime import datetime, date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.accounts.models import UserRole
from apps.core.models import SiteConfiguration, HomepageConfig, ActivityLog, PublishableStatus
from apps.teachings.models import Sermon, SermonSeries, SermonCategory, SermonScripture
from apps.publications.models import Publication, PublicationCategory, PublicationType
from apps.people.models import Person
from apps.ministries.models import Ministry, ChurchMeeting, ChurchLocation
from apps.events.models import Event, EventCategory
from apps.conferences.models import Conference
from apps.articles.models import Article
from apps.announcements.models import Announcement
from apps.streaming.models import LiveStreamChannel, StreamStatus
from apps.website.models import ContactMessage, PrayerRequest, NewsletterSubscriber

User = get_user_model()


class CityGateCMSTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Users
        self.superadmin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@thecitygatechurch.org",
            password="SecurePassword123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.content_manager = User.objects.create_user(
            username="contentmanager",
            email="content@thecitygatechurch.org",
            password="SecurePassword123!",
            role=UserRole.CONTENT_MANAGER,
        )
        self.member = User.objects.create_user(
            username="churchmember",
            email="member@thecitygatechurch.org",
            password="SecurePassword123!",
            role=UserRole.MEMBER,
        )

        # Create baseline person
        self.pastor = Person.objects.create(
            name="Pastor Samuel Adebayo",
            title="Senior Pastor",
            biography="Founding pastor of The CityGate Church.",
        )

        # Create dummy PDF
        self.dummy_pdf = SimpleUploadedFile("journal_vol4.pdf", b"%PDF-1.4 dummy pdf content for testing", content_type="application/pdf")

    # 1. PERMISSIONS & RBAC
    def test_unauthenticated_user_redirected(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_non_staff_member_forbidden(self):
        self.client.login(username="churchmember", password="SecurePassword123!")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("website:home"))

    def test_staff_user_can_access_dashboard(self):
        self.client.login(username="contentmanager", password="SecurePassword123!")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Executive Overview")

    # 2. TEACHINGS MANAGEMENT & AUDIT LOGGING
    def test_teaching_creation_and_activity_log(self):
        self.client.login(username="contentmanager", password="SecurePassword123!")
        
        post_data = {
            "title": "Unveiling the Supernatural",
            "speaker": self.pastor.pk,
            "preached_date": "2026-03-15",
            "summary": "Deep insight into kingdom faith and spiritual authority.",
            "status": PublishableStatus.PUBLISHED,
            "scripture_book[]": ["Romans", "Hebrews"],
            "scripture_chapter[]": ["8", "11"],
            "scripture_verse_start[]": ["28", "1"],
            "scripture_verse_end[]": ["30", "6"],
            "scripture_text[]": ["All things work together for good.", "Now faith is the substance."],
        }
        response = self.client.post(reverse("dashboard:teaching_create"), post_data)
        self.assertEqual(response.status_code, 302)
        
        sermon = Sermon.objects.filter(title="Unveiling the Supernatural").first()
        self.assertIsNotNone(sermon)
        self.assertEqual(sermon.speaker, self.pastor)
        self.assertEqual(sermon.scriptures.count(), 2)
        
        # Verify Activity Log was recorded
        log = ActivityLog.objects.filter(model_name="Sermon", object_id=str(sermon.pk)).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, ActivityLog.Action.CREATED)

    def test_teaching_quick_actions(self):
        self.client.login(username="contentmanager", password="SecurePassword123!")
        sermon = Sermon.objects.create(
            title="The Mystery of Divine Grace",
            preached_date=date.today(),
            status=PublishableStatus.DRAFT,
        )
        
        # Fast publish
        self.client.post(reverse("dashboard:teaching_action", kwargs={"pk": sermon.pk, "action": "publish"}))
        sermon.refresh_from_db()
        self.assertEqual(sermon.status, PublishableStatus.PUBLISHED)
        
        # Fast duplicate
        self.client.post(reverse("dashboard:teaching_action", kwargs={"pk": sermon.pk, "action": "duplicate"}))
        duplicated = Sermon.objects.filter(title="The Mystery of Divine Grace (Copy)").first()
        self.assertIsNotNone(duplicated)
        self.assertEqual(duplicated.status, PublishableStatus.DRAFT)

    # 3. PUBLICATIONS & JOURNALS WORKFLOW (HIGH PRIORITY)
    def test_publication_journal_full_lifecycle(self):
        self.client.login(username="superadmin", password="SecurePassword123!")
        
        # 1. Admin creates a Journal
        post_data = {
            "title": "Apostolic Voice Journal",
            "publication_type": PublicationType.JOURNAL,
            "edition_volume": "Vol. 6 Issue 1 (Spring 2026)",
            "author_name": "Pastoral Theological Council",
            "description": "Comprehensive theological reflections and prophetic directions for the body of Christ.",
            "publication_date": "2026-03-01",
            "pdf_file": self.dummy_pdf,
            "status": PublishableStatus.PUBLISHED,
            "is_downloadable": True,
        }
        response = self.client.post(reverse("dashboard:publication_create"), post_data)
        self.assertEqual(response.status_code, 302)

        journal = Publication.objects.filter(title="Apostolic Voice Journal").first()
        self.assertIsNotNone(journal)
        self.assertEqual(journal.publication_type, PublicationType.JOURNAL)
        self.assertEqual(journal.download_count, 0)

        # 2. Public user views publications list
        self.client.logout()
        resp_list = self.client.get(reverse("website:publications_list"))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, "Apostolic Voice Journal")
        self.assertContains(resp_list, "Vol. 6 Issue 1 (Spring 2026)")

        # 3. Public user views publication detail
        resp_detail = self.client.get(reverse("website:publication_detail", kwargs={"slug": journal.slug}))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, "Pastoral Theological Council")

        # 4. Public user downloads PDF -> Download telemetry increments
        resp_dl = self.client.get(reverse("website:publication_download", kwargs={"slug": journal.slug}))
        self.assertEqual(resp_dl.status_code, 200)
        self.assertEqual(resp_dl["Content-Type"], "application/pdf")
        
        journal.refresh_from_db()
        self.assertEqual(journal.download_count, 1)

    # 4. MINISTRIES, MEETINGS & LOCATIONS
    def test_ministry_and_recurring_meetings_crud(self):
        self.client.login(username="superadmin", password="SecurePassword123!")
        
        # Create Campus Location
        loc = ChurchLocation.objects.create(
            name="Main Island Campus",
            address="10 Kingdom Way, Lekki",
            city="Lagos",
            is_main_campus=True,
        )

        # Create Ministry
        min_obj = Ministry.objects.create(
            name="CityGate Youth Ministry",
            tagline="Ignited for Kingdom Dominion",
            leader=self.pastor,
            meeting_schedule="Fridays at 5:00 PM",
        )

        # Create Recurring Meeting
        meeting_data = {
            "name": "Friday Youth Revival Service",
            "ministry": min_obj.pk,
            "location": loc.pk,
            "day_of_week": 5, # Friday
            "start_time": "17:00",
            "end_time": "19:00",
            "location_hall": "Youth Chapel",
            "is_online": True,
            "is_active": True,
        }
        res = self.client.post(reverse("dashboard:meeting_create"), meeting_data)
        self.assertEqual(res.status_code, 302)
        
        meeting = ChurchMeeting.objects.filter(name="Friday Youth Revival Service").first()
        self.assertIsNotNone(meeting)
        self.assertEqual(meeting.location, loc)

    # 5. LIVE STREAMING CONTROL CENTER
    def test_live_stream_control_center(self):
        self.client.login(username="superadmin", password="SecurePassword123!")
        
        post_data = {
            "title": "Sunday Divine Encounter Service",
            "platform": "youtube",
            "stream_status": StreamStatus.LIVE,
            "stream_url": "https://www.youtube.com/watch?v=live123",
            "current_program": "Sunday Divine Encounter Service",
            "current_topic": "Walking in Dominion",
            "current_speaker": "Pastor Samuel Adebayo",
            "viewer_count": 1500,
        }
        res = self.client.post(reverse("dashboard:live_stream"), post_data)
        self.assertEqual(res.status_code, 302)
        
        channel = LiveStreamChannel.load()
        self.assertEqual(channel.stream_status, StreamStatus.LIVE)
        self.assertTrue(channel.is_live)
        self.assertEqual(channel.current_topic, "Walking in Dominion")

    # 6. COMMUNICATIONS: CONTACT MESSAGES & CONFIDENTIAL PRAYER REQUESTS
    def test_public_contact_and_prayer_request_submission(self):
        # 1. Visitor submits contact inquiry
        contact_data = {
            "form_type": "contact",
            "full_name": "Sister Grace Oladipo",
            "email": "grace@example.com",
            "phone": "+2348011223344",
            "subject": "Counseling Session Request",
            "message": "I would like to speak with a pastor regarding family counseling.",
        }
        res = self.client.post(reverse("website:contact"), contact_data)
        self.assertEqual(res.status_code, 302)
        
        msg = ContactMessage.objects.filter(email="grace@example.com").first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.status, "new")

        # 2. Visitor submits prayer request
        prayer_data = {
            "form_type": "prayer",
            "full_name": "Brother Michael",
            "email": "michael@example.com",
            "prayer_point": "Please pray for healing and divine breakthrough in my health.",
        }
        res_p = self.client.post(reverse("website:contact"), prayer_data)
        self.assertEqual(res_p.status_code, 302)
        
        prayer = PrayerRequest.objects.filter(full_name="Brother Michael").first()
        self.assertIsNotNone(prayer)
        self.assertTrue(prayer.is_confidential)

        # 3. Staff handles prayer request
        self.client.login(username="superadmin", password="SecurePassword123!")
        self.client.post(reverse("dashboard:prayer_requests"), {
            "prayer_id": prayer.pk,
            "action": "mark_handled",
            "pastoral_notes": "Prayed with brother during evening watch.",
        })
        prayer.refresh_from_db()
        self.assertEqual(prayer.status, "handled")
        self.assertEqual(prayer.handled_by, self.superadmin)

    # 7. NEWSLETTER SUBSCRIPTION & CSV EXPORT
    def test_newsletter_subscription_and_export(self):
        # 1. Public subscribe
        res = self.client.post(reverse("website:newsletter_subscribe"), {"email": "believer@example.com"})
        self.assertEqual(res.status_code, 302)
        
        sub = NewsletterSubscriber.objects.filter(email="believer@example.com").first()
        self.assertIsNotNone(sub)
        self.assertTrue(sub.is_active)

        # 2. Staff exports CSV
        self.client.login(username="superadmin", password="SecurePassword123!")
        csv_res = self.client.get(reverse("dashboard:subscribers_export"))
        self.assertEqual(csv_res.status_code, 200)
        self.assertEqual(csv_res["Content-Type"], "text/csv")
        self.assertIn(b"believer@example.com", csv_res.content)
