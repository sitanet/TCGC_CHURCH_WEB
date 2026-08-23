"""
Unit tests for custom User model, roles, and authentication.
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, UserRole


class AccountsAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@thecitygatechurch.org",
            password="SecurePassword123!",
        )
        self.pastor = User.objects.create_user(
            username="pastor_sam",
            email="pastor.sam@thecitygatechurch.org",
            password="SecurePassword123!",
            role=UserRole.PASTOR_STAFF,
            first_name="Samuel",
            last_name="David",
            title="Resident Pastor",
        )
        self.member = User.objects.create_user(
            username="member_john",
            email="john@example.com",
            password="SecurePassword123!",
            role=UserRole.MEMBER,
            first_name="John",
            last_name="Doe",
        )

    def test_user_creation_and_roles(self):
        self.assertTrue(self.super_admin.is_super_admin)
        self.assertTrue(self.super_admin.is_staff_member)
        
        self.assertTrue(self.pastor.is_pastoral_staff)
        self.assertTrue(self.pastor.is_staff_member)
        self.assertFalse(self.pastor.is_super_admin)

        self.assertFalse(self.member.is_staff_member)
        self.assertEqual(self.member.role, UserRole.MEMBER)

    def test_login_flow(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "pastor_sam", "password": "SecurePassword123!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_dashboard_access_protection(self):
        # Anonymous user must be redirected to login
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)

        # Member user without staff permissions must be redirected
        self.client.login(username="member_john", password="SecurePassword123!")
        member_response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(member_response.status_code, 302)

        # Pastor staff user can access dashboard
        self.client.login(username="pastor_sam", password="SecurePassword123!")
        staff_response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(staff_response.status_code, 200)
        self.assertContains(staff_response, "Executive Overview")
