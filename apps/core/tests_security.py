"""
Dedicated Security, RBAC, File Upload, and Anti-Spam Automated Test Suite
for The CityGate Church Platform.
"""
from io import BytesIO
from datetime import date, datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.accounts.models import UserRole
from apps.core.models import SiteConfiguration, HomepageConfig, PublishableStatus
from apps.core.validators import (
    validate_image_file, validate_document_file, validate_audio_file, validate_video_file,
    sanitize_filename, FORBIDDEN_EXTENSIONS
)
from apps.teachings.models import Sermon, SermonSeries
from apps.publications.models import Publication, PublicationType
from apps.articles.models import Article
from apps.events.models import Event
from apps.website.models import ContactMessage, PrayerRequest, NewsletterSubscriber

User = get_user_model()


class CityGateSecurityAndRBACTests(TestCase):
    """
    Automated security tests verifying RBAC authorization, confidential information protection,
    file validation, honeypot anti-spam, and draft isolation.
    """

    def setUp(self):
        # 1. Setup users with various roles
        self.superadmin = User.objects.create_superuser(
            username="super_admin_sec",
            email="superadmin@citygate.test",
            password="SecurePassword123!",
            role=UserRole.SUPER_ADMIN,
        )
        self.pastor = User.objects.create_user(
            username="pastor_sec",
            email="pastor@citygate.test",
            password="SecurePassword123!",
            role=UserRole.PASTOR_STAFF,
            is_staff=True,
        )
        self.content_mgr = User.objects.create_user(
            username="content_mgr_sec",
            email="content@citygate.test",
            password="SecurePassword123!",
            role=UserRole.CONTENT_MANAGER,
            is_staff=True,
        )
        self.media_lead = User.objects.create_user(
            username="media_lead_sec",
            email="media@citygate.test",
            password="SecurePassword123!",
            role=UserRole.MEDIA_LEAD,
            is_staff=True,
        )
        self.regular_member = User.objects.create_user(
            username="member_sec",
            email="member@citygate.test",
            password="SecurePassword123!",
            role=UserRole.MEMBER,
            is_staff=False,
        )

        # 2. Setup Confidential Records
        self.prayer = PrayerRequest.objects.create(
            full_name="Sister Grace Confidential",
            email="grace@example.com",
            prayer_point="Deep personal intercessory prayer request regarding family restoration.",
            is_confidential=True,
        )
        self.contact_msg = ContactMessage.objects.create(
            full_name="Inquirer John",
            email="john@example.com",
            subject="Personal pastoral counsel",
            message="Private inquiry for senior pastoral team.",
        )

        # 3. Setup Published vs Draft Content
        self.published_sermon = Sermon.objects.create(
            title="Published Word of Life",
            slug="published-word-of-life",
            status=PublishableStatus.PUBLISHED,
            preached_date=date.today(),
        )
        self.draft_sermon = Sermon.objects.create(
            title="Confidential Internal Draft Sermon Notes",
            slug="confidential-internal-draft-sermon-notes",
            status=PublishableStatus.DRAFT,
            preached_date=date.today(),
        )

        self.published_article = Article.objects.create(
            title="Published Kingdom Perspective",
            slug="published-kingdom-perspective",
            status=PublishableStatus.PUBLISHED,
            body="Public content...",
        )
        self.draft_article = Article.objects.create(
            title="Unpublished Draft Article Spec",
            slug="unpublished-draft-article-spec",
            status=PublishableStatus.DRAFT,
            body="Confidential draft...",
        )

    # --------------------------------------------------------------------------
    # A. RBAC & CONFIDENTIAL INFORMATION ISOLATION
    # --------------------------------------------------------------------------

    def test_unauthenticated_user_cannot_access_dashboard(self):
        """Unauthenticated requests to dashboard redirect to login."""
        client = Client()
        res = client.get(reverse("dashboard:index"))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(reverse("accounts:login") in res.url)

    def test_regular_member_cannot_access_dashboard(self):
        """Regular non-staff members are denied access to dashboard."""
        client = Client()
        client.force_login(self.regular_member)
        res = client.get(reverse("dashboard:index"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("website:home"))

    def test_media_lead_cannot_access_confidential_prayer_requests(self):
        """Media Lead or other non-pastoral staff cannot view confidential prayer requests."""
        client = Client()
        client.force_login(self.media_lead)
        res = client.get(reverse("dashboard:prayer_requests"))
        # Should redirect to dashboard:index due to insufficient role
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("dashboard:index"))

    def test_content_manager_cannot_access_confidential_contact_messages(self):
        """Content Manager cannot access pastoral contact messages."""
        client = Client()
        client.force_login(self.content_mgr)
        res = client.get(reverse("dashboard:contact_messages"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("dashboard:index"))

    def test_content_manager_cannot_access_user_management(self):
        """Non-admin staff cannot manage staff accounts."""
        client = Client()
        client.force_login(self.content_mgr)
        res = client.get(reverse("dashboard:users_list"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("dashboard:index"))

    def test_pastor_staff_can_access_prayer_requests(self):
        """Pastor Staff has legitimate access to pastoral intercession inbox."""
        client = Client()
        client.force_login(self.pastor)
        res = client.get(reverse("dashboard:prayer_requests"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Sister Grace Confidential")

    def test_super_admin_can_access_all_modules(self):
        """Super Admin has full authorized access to system settings and communications."""
        client = Client()
        client.force_login(self.superadmin)
        res1 = client.get(reverse("dashboard:prayer_requests"))
        res2 = client.get(reverse("dashboard:users_list"))
        res3 = client.get(reverse("dashboard:website_settings"))
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res3.status_code, 200)

    # --------------------------------------------------------------------------
    # B. FILE UPLOAD SECURITY VALIDATORS
    # --------------------------------------------------------------------------

    def test_validate_image_rejects_executable_files(self):
        """Executable files masked as images are rejected."""
        malicious_file = SimpleUploadedFile("exploit.exe", b"MZ\x90\x00BinaryData", content_type="application/octet-stream")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(malicious_file)
        self.assertEqual(ctx.exception.code, "forbidden_extension")

    def test_validate_image_rejects_script_files(self):
        """Script files like .php, .py, .sh are rejected."""
        for dangerous_ext in [".php", ".py", ".sh", ".vbs", ".js"]:
            bad_file = SimpleUploadedFile(f"shell{dangerous_ext}", b"echo 'hacked'", content_type="text/plain")
            with self.assertRaises(ValidationError):
                validate_image_file(bad_file)

    def test_validate_image_rejects_oversized_file(self):
        """Image files exceeding 5MB are rejected."""
        huge_file = SimpleUploadedFile("huge.jpg", b"0" * (6 * 1024 * 1024), content_type="image/jpeg")
        with self.assertRaises(ValidationError) as ctx:
            validate_image_file(huge_file)
        self.assertEqual(ctx.exception.code, "file_too_large")

    def test_validate_image_accepts_valid_jpeg(self):
        """Valid JPEG images under 5MB are accepted."""
        valid_img = SimpleUploadedFile("cover.jpg", b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00", content_type="image/jpeg")
        # Should not raise exception
        validate_image_file(valid_img)

    def test_sanitize_filename_removes_path_traversal(self):
        """Path traversal sequences (../../) and unsafe characters are neutralized."""
        self.assertEqual(sanitize_filename("../../etc/passwd"), "passwd")
        self.assertEqual(sanitize_filename("..\\..\\windows\\system32.dll"), "system32.dll")
        self.assertEqual(sanitize_filename("my file $!# name.jpg"), "my_file_name.jpg")

    # --------------------------------------------------------------------------
    # C. HONEYPOT ANTI-SPAM DEFENSE
    # --------------------------------------------------------------------------

    def test_contact_form_honeypot_rejects_spambots(self):
        """Spam bots filling the hidden honeypot field are silently dropped."""
        client = Client()
        initial_count = ContactMessage.objects.count()
        res = client.post(reverse("website:contact"), {
            "full_name": "Spam Bot",
            "email": "bot@spammer.test",
            "subject": "Buy cheap stuff",
            "message": "Spam payload http://spamlink.test",
            "hp_website": "http://botfilledthis.com",  # Honeypot filled
        })
        self.assertEqual(res.status_code, 302)
        # Message was NOT written to database
        self.assertEqual(ContactMessage.objects.count(), initial_count)

    def test_prayer_form_honeypot_rejects_spambots(self):
        """Spam bots targeting the prayer portal are silently dropped."""
        client = Client()
        initial_count = PrayerRequest.objects.count()
        res = client.post(reverse("website:prayer_request"), {
            "full_name": "Prayer Spammer",
            "email": "spam@spammer.test",
            "prayer_point": "Spam payload here",
            "hp_website": "http://spambot.test",  # Honeypot filled
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(PrayerRequest.objects.count(), initial_count)

    # --------------------------------------------------------------------------
    # D. DRAFT & UNPUBLISHED CONTENT ISOLATION
    # --------------------------------------------------------------------------

    def test_public_teachings_list_never_contains_drafts(self):
        """Public teaching archive only lists published teachings."""
        client = Client()
        res = client.get(reverse("website:teachings_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Published Word of Life")
        self.assertNotContains(res, "Confidential Internal Draft Sermon Notes")

    def test_public_articles_list_never_contains_drafts(self):
        """Public articles directory only lists published articles."""
        client = Client()
        res = client.get(reverse("website:articles_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Published Kingdom Perspective")
        self.assertNotContains(res, "Unpublished Draft Article Spec")

    def test_public_search_api_never_returns_drafts(self):
        """Global search API strictly excludes unpublished items."""
        client = Client()
        res = client.get(reverse("api_v1:api_root") + "search/query/?q=Confidential")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_results"], 0)
