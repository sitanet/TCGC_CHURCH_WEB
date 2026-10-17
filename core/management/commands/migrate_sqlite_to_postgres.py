import os
import sqlite3
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ConferenceRegistration


class Command(BaseCommand):
    help = "Migrates all legacy conference registrations from db.sqlite3 into the PostgreSQL imgc_registrations table"

    def add_arguments(self, parser):
        parser.add_argument(
            '--sqlite-path',
            type=str,
            default=str(settings.BASE_DIR / 'db.sqlite3'),
            help='Path to db.sqlite3'
        )

    def handle(self, *args, **options):
        sqlite_path = options['sqlite_path']
        if not os.path.exists(sqlite_path):
            self.stdout.write(self.style.ERROR(f"SQLite database not found at {sqlite_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Opening SQLite database at: {sqlite_path}"))
        con = sqlite3.connect(sqlite_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Check if core_conferenceregistration exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('core_conferenceregistration', 'imgc_registrations')")
        tables = [r[0] for r in cur.fetchall()]
        table_name = 'core_conferenceregistration' if 'core_conferenceregistration' in tables else ('imgc_registrations' if 'imgc_registrations' in tables else None)

        if not table_name:
            self.stdout.write(self.style.WARNING("No registration tables found in SQLite database."))
            con.close()
            return

        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        self.stdout.write(self.style.NOTICE(f"Found {len(rows)} records in SQLite {table_name}"))

        imported = 0
        skipped = 0

        for row in rows:
            row_dict = dict(row)
            code = (row_dict.get('registration_code') or '').strip()
            email = (row_dict.get('email') or '').strip().lower()
            phone = (row_dict.get('phone_number') or '').strip()

            # Check if record already exists in current database (PostgreSQL)
            existing = None
            if code:
                existing = ConferenceRegistration.objects.filter(registration_code=code).first()
            if not existing and email:
                existing = ConferenceRegistration.objects.filter(email__iexact=email).first()

            if existing:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Skipped (already exists): {code or email}"))
                continue

            raw_mode = (row_dict.get('attendance_mode') or 'camping').strip()
            mode_map = {
                'onsite_camp': 'camping',
                'camping': 'camping',
                'physical_day': 'non_camping',
                'non_camping': 'non_camping',
                'virtual_streaming': 'online',
                'online': 'online',
            }
            attendance_mode = mode_map.get(raw_mode, raw_mode or 'camping')

            raw_amount = row_dict.get('amount_paid') or 0.00
            try:
                amount_paid = Decimal(str(raw_amount))
            except Exception:
                amount_paid = Decimal('0.00')

            is_first_time = bool(row_dict.get('is_first_time') or row_dict.get('first_time_attending'))
            notes = row_dict.get('special_notes') or row_dict.get('expectation') or ''

            ConferenceRegistration.objects.create(
                registration_code=code,
                surname=row_dict.get('surname') or '',
                first_name=row_dict.get('first_name') or '',
                email=email,
                phone_number=phone,
                gender=(row_dict.get('gender') or 'male').strip().lower(),
                age_range=row_dict.get('age_range') or '26_35',
                designation=row_dict.get('designation') or 'working_professional',
                other_designation=row_dict.get('other_designation') or '',
                city=row_dict.get('city') or '',
                state=row_dict.get('state') or '',
                country=row_dict.get('country') or 'Nigeria',
                is_first_time=is_first_time,
                attendance_mode=attendance_mode,
                feeding_subscription=row_dict.get('feeding_subscription') or 'none',
                feeding_days=row_dict.get('feeding_days') or '',
                special_notes=notes,
                requires_code_dispatch=bool(row_dict.get('requires_code_dispatch')),
                dispatch_phone_target=row_dict.get('dispatch_phone_target') or '',
                is_verified=bool(row_dict.get('is_verified')),
                amount_paid=amount_paid,
                payment_reference=row_dict.get('payment_reference') or '',
                has_checked_in=bool(row_dict.get('has_checked_in')),
                ip_address=row_dict.get('ip_address'),
                user_agent=row_dict.get('user_agent'),
            )
            imported += 1
            self.stdout.write(self.style.SUCCESS(f"Imported into PostgreSQL: {code} - {row_dict.get('first_name')} {row_dict.get('surname')}"))

        con.close()
        self.stdout.write(self.style.SUCCESS(f"\nMigration finished: {imported} imported, {skipped} skipped."))
