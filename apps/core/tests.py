"""
Unit tests for core views, public pages, and DRF API v1 endpoints.
"""
from django.test import TestCase, Client
from django.urls import reverse


class CoreAndApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_public_pages_render(self):
        pages = [
            ("website:home", 200),
            ("website:about", 200),
            ("website:visit", 200),
            ("website:contact", 200),
            ("accounts:login", 200),
        ]
        for url_name, expected_status in pages:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, expected_status)
                self.assertContains(response, "THE CITYGATE")

    def test_api_health_endpoint(self):
        response = self.client.get(reverse("api_v1:api_health"))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "healthy")
        self.assertEqual(json_data.get("version"), "1.0.0")

    def test_api_root_endpoint(self):
        response = self.client.get(reverse("api_v1:api_root"))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("endpoints", json_data)
        self.assertIn("teachings", json_data["endpoints"])
        self.assertIn("events", json_data["endpoints"])
        self.assertIn("streaming_status", json_data["endpoints"])

    def test_api_search_endpoint(self):
        response = self.client.get(reverse("api_v1:search:unified_search") + "?q=worship")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "success")
        self.assertIn("results", json_data)
