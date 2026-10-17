from django.test import TestCase
from django.urls import reverse
from .models import ConferenceRegistration, OnlineGiving, NewsletterSubscriber


class TCGCWebsiteTests(TestCase):
    def test_all_pages_render_200(self):
        for route_name in ['home', 'registration', 'video_streaming', 'audio_streaming', 'ministries']:
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, 200, f"Route {route_name} failed")

    def test_conference_registration_submission(self):
        response = self.client.post(
            reverse('registration'),
            {
                'surname': 'Adeleke',
                'first_name': 'Emmanuel',
                'email': 'adeleke@example.com',
                'phone_country_code': '+234',
                'phone_number': '8012345678',
                'gender': 'Male',
                'age_range': '20 - 29',
                'designation': 'Member',
                'city': 'Ibadan',
                'state': 'Oyo State',
                'country': 'Nigeria',
                'first_time_attending': 'no',
                'attendance_mode': 'onsite_camp',
                'expectation': 'Spiritual growth and encounter.',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConferenceRegistration.objects.count(), 1)
        reg = ConferenceRegistration.objects.first()
        self.assertEqual(reg.surname, 'Adeleke')
        self.assertEqual(reg.attendance_mode, 'onsite_camp')

    def test_online_giving_submission(self):
        response = self.client.post(
            reverse('home'),
            {
                'form_type': 'give_online',
                'first_name': 'Fisayo',
                'last_name': 'Elugbadebo',
                'email': 'fisayo@example.com',
                'phone_country_code': '+234',
                'phone_number': '7012345678',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(OnlineGiving.objects.count(), 1)

    def test_newsletter_subscription(self):
        response = self.client.post(
            reverse('subscribe_newsletter'),
            {'email': 'believer@citygate.org'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
