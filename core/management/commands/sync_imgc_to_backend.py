import json
import logging
import requests
from django.core.management.base import BaseCommand
from core.models import ConferenceRegistration

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Syncs IMGC registrations stored in SQLite directly into TCGC_BACKEND PostgreSQL database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--backend-url',
            type=str,
            default='http://127.0.0.1:8000/api/v1/imgc/register/',
            help='Backend registration API endpoint'
        )
        parser.add_argument(
            '--fallback-url',
            type=str,
            default='https://tcgc.thecitygatechurch.org/api/v1/imgc/register/',
            help='Fallback public endpoint if localhost is unreachable'
        )

    def handle(self, *args, **options):
        primary_url = options['backend_url']
        fallback_url = options['fallback_url']

        registrations = ConferenceRegistration.objects.all().order_by('created_at')
        total = registrations.count()
        self.stdout.write(self.style.NOTICE(f"Found {total} registrations to check and sync..."))

        synced = 0
        already_exist = 0
        errors = 0

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TCGC-Website-Sync/1.0',
        }

        for reg in registrations:
            payload = {
                'registration_code': reg.registration_code,
                'surname': reg.surname,
                'first_name': reg.first_name,
                'email': reg.email,
                'phone_country_code': getattr(reg, 'phone_country_code', '+234') or '+234',
                'phone_number': reg.phone_number,
                'gender': reg.gender,
                'age_range': reg.age_range,
                'designation': reg.designation,
                'other_designation': getattr(reg, 'other_designation', '') or '',
                'city': reg.city,
                'state': getattr(reg, 'state', '') or '',
                'country': getattr(reg, 'country', 'Nigeria') or 'Nigeria',
                'is_first_time': 'yes' if getattr(reg, 'is_first_time', False) else 'no',
                'attendance_mode': reg.attendance_mode,
                'feeding_subscription': getattr(reg, 'feeding_subscription', 'none') or 'none',
                'feeding_days': getattr(reg, 'feeding_days', '') or '',
                'special_notes': getattr(reg, 'special_notes', '') or getattr(reg, 'expectation', '') or '',
            }

            resp = None
            used_url = primary_url
            try:
                resp = requests.post(primary_url, json=payload, headers=headers, timeout=5)
            except Exception:
                try:
                    used_url = fallback_url
                    resp = requests.post(fallback_url, json=payload, headers=headers, timeout=6)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to reach backend for {reg.registration_code}: {e}"))
                    errors += 1
                    continue

            if resp:
                if resp.status_code in [200, 201]:
                    synced += 1
                    data = resp.json()
                    backend_code = data.get('registration_code') or reg.registration_code
                    self.stdout.write(self.style.SUCCESS(f"Synced: {reg.first_name} {reg.surname} -> {backend_code}"))
                elif resp.status_code == 400:
                    try:
                        data = resp.json()
                        if data.get('existing_code'):
                            already_exist += 1
                            self.stdout.write(self.style.WARNING(f"Already in backend: {reg.first_name} {reg.surname} ({data.get('existing_code')})"))
                        else:
                            self.stdout.write(self.style.ERROR(f"Validation error for {reg.registration_code}: {data.get('errors')}"))
                            errors += 1
                    except Exception:
                        errors += 1
                else:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"HTTP {resp.status_code} for {reg.registration_code} from {used_url}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nSync Complete! Newly Synced: {synced}, Already existed: {already_exist}, Errors: {errors}"
        ))
