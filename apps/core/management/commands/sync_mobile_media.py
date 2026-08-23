"""
Management command to sync live media, sermons, audio streams, speakers,
devotional publications, and events from the Citygate mobile backend
(https://tcgc.thecitygatechurch.org/api/) directly into the Django database.
"""
import urllib.request
import json
import ssl
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.people.models import Person, LeadershipCategory
from apps.teachings.models import Sermon, SermonCategory, SermonSeries
from apps.publications.models import Publication, PublicationCategory, PublicationType
from apps.events.models import Event, EventCategory
from apps.core.models import PublishableStatus


class Command(BaseCommand):
    help = "Sync authentic media, sermons, audio streams, publications, and events from mobile backend"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting sync from tcgc.thecitygatechurch.org/api/ ..."))

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        def fetch_all(endpoint):
            url = f"https://tcgc.thecitygatechurch.org/api/{endpoint}/"
            items = []
            while url:
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    res = json.loads(urllib.request.urlopen(req, context=ctx).read().decode('utf-8'))
                    if isinstance(res, dict) and 'results' in res:
                        items.extend(res['results'])
                        url = res.get('next')
                    elif isinstance(res, list):
                        items.extend(res)
                        break
                    else:
                        break
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error fetching {url}: {e}"))
                    break
            return items

        # 1. SYNC LEADERSHIP CATEGORIES & SPEAKERS
        self.stdout.write("--> Syncing Speakers & Pastoral Ministers...")
        pastoral_cat, _ = LeadershipCategory.objects.get_or_create(
            name="Pastoral Leadership",
            defaults={"description": "Senior and resident pastors of The CityGate Church."}
        )
        ministers_cat, _ = LeadershipCategory.objects.get_or_create(
            name="Ministers & Ministry Leaders",
            defaults={"description": "Ministry leaders, guest speakers, and department heads."}
        )

        speaker_map = {}  # name -> Person instance
        speakers_data = fetch_all("speakers")
        for s in speakers_data:
            name = (s.get("name") or "").strip()
            if not name:
                continue
            title = (s.get("title") or "Pastor").strip()
            cat = pastoral_cat if "pastor" in title.lower() or "rev" in title.lower() else ministers_cat
            photo_url = s.get("image") or s.get("image_url") or ""
            
            slug = slugify(name)
            person, created = Person.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "title": title,
                    "category": cat,
                    "photo_url": photo_url if photo_url and photo_url != "None" else "",
                    "status": PublishableStatus.PUBLISHED,
                }
            )
            if not created:
                person.name = name
                person.title = title
                if photo_url and photo_url != "None":
                    person.photo_url = photo_url
                person.save()
            speaker_map[name.lower()] = person
            speaker_map[s.get("id")] = person

        self.stdout.write(self.style.SUCCESS(f"Synced {len(speakers_data)} speakers successfully."))

        # 2. SYNC MESSAGE CATEGORIES & SERMON SERIES
        self.stdout.write("--> Syncing Sermon Categories & Series...")
        cat_map = {}
        cats_data = fetch_all("message-categories")
        for c in cats_data:
            cat_name = (c.get("name") or "").strip()
            if not cat_name:
                continue
            cat_slug = slugify(cat_name)
            s_cat, _ = SermonCategory.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": cat_name, "description": f"Teachings and messages from {cat_name}"}
            )
            cat_map[c.get("id")] = s_cat
            cat_map[cat_name.lower()] = s_cat

            # Also create corresponding SermonSeries for major series
            s_series, _ = SermonSeries.objects.get_or_create(
                slug=cat_slug,
                defaults={
                    "title": cat_name,
                    "description": f"Thematic sermon series: {cat_name}",
                    "status": PublishableStatus.PUBLISHED,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Synced {len(cats_data)} sermon categories."))

        # 3. SYNC EBOOKS & THE GLORY JOURNAL PUBLICATIONS
        self.stdout.write("--> Syncing E-books & Publications...")
        pub_cat, _ = PublicationCategory.objects.get_or_create(
            name="The Glory Journal",
            defaults={"description": "Quarterly church publication and spiritual growth journal."}
        )

        ebooks_data = fetch_all("ebooks")
        for eb in ebooks_data:
            title = (eb.get("title") or "").strip()
            if not title:
                continue
            pdf_url = eb.get("file") or eb.get("file_download_url") or ""
            cover_url = eb.get("cover_image") or eb.get("cover_image_url") or ""
            author = (eb.get("author") or "The Citygate Church").strip()
            desc = (eb.get("description") or "").replace("\r\n", "\n").strip()
            
            # parse date
            pub_date = None
            if eb.get("date"):
                try:
                    pub_date = datetime.fromisoformat(eb.get("date").replace("Z", "+00:00")).date()
                except Exception:
                    pub_date = date.today()

            pub_slug = slugify(f"glory-journal-{title}")
            pub, created = Publication.objects.get_or_create(
                slug=pub_slug,
                defaults={
                    "title": f"The Glory Journal: {title}",
                    "publication_type": PublicationType.JOURNAL,
                    "edition_volume": title,
                    "category": pub_cat,
                    "author_name": author,
                    "description": desc,
                    "publication_date": pub_date or date.today(),
                    "pdf_url": pdf_url,
                    "cover_image_url": cover_url,
                    "is_downloadable": True,
                    "status": PublishableStatus.PUBLISHED,
                    "is_featured": True,
                }
            )
            if not created:
                pub.pdf_url = pdf_url
                pub.cover_image_url = cover_url
                pub.description = desc
                pub.save()

        self.stdout.write(self.style.SUCCESS(f"Synced {len(ebooks_data)} publications."))

        # 4. SYNC REAL SERMONS & MESSAGES
        self.stdout.write("--> Syncing 200 Real Sermons & Audio Media...")
        messages_data = fetch_all("messages")
        synced_sermons_count = 0
        for m in messages_data:
            title = (m.get("title") or "").strip()
            if not title:
                continue
            
            # Audio & Cover URLs
            audio_url = m.get("audio_file") or m.get("audio_url") or ""
            cover_url = m.get("image") or m.get("image_url") or ""
            video_url = m.get("video_url") or ""
            
            # Category
            cat_id = m.get("category")
            cat_name = (m.get("category_name") or "").strip()
            category_obj = cat_map.get(cat_id) or cat_map.get(cat_name.lower())
            
            # Series
            series_obj = None
            if category_obj:
                series_obj = SermonSeries.objects.filter(slug=category_obj.slug).first()

            # Speaker
            speaker_str = (m.get("speaker") or "Pastor").strip()
            speaker_obj = speaker_map.get(speaker_str.lower())
            if not speaker_obj:
                # search partial
                for k, v in speaker_map.items():
                    if isinstance(k, str) and k in speaker_str.lower():
                        speaker_obj = v
                        break

            # Date
            preached_date = date.today()
            if m.get("date"):
                try:
                    preached_date = datetime.fromisoformat(m.get("date").replace("Z", "+00:00")).date()
                except Exception:
                    pass

            s_slug = slugify(f"{title}-{preached_date.strftime('%Y%m%d')}")
            # Ensure unique slug
            if Sermon.objects.filter(slug=s_slug).exists():
                s_slug = f"{s_slug}-{m.get('id')}"

            sermon, created = Sermon.objects.get_or_create(
                slug=s_slug,
                defaults={
                    "title": title,
                    "speaker": speaker_obj,
                    "speaker_name": speaker_str,
                    "category": category_obj,
                    "series": series_obj,
                    "preached_date": preached_date,
                    "summary": f"Sermon delivered by {speaker_str} on {preached_date.strftime('%B %d, %Y')}.",
                    "audio_url": audio_url,
                    "cover_image_url": cover_url,
                    "video_url": video_url if video_url and video_url != "None" else "",
                    "status": PublishableStatus.PUBLISHED,
                    "is_featured": (synced_sermons_count == 0),
                }
            )
            if not created:
                sermon.audio_url = audio_url
                sermon.cover_image_url = cover_url
                sermon.speaker = speaker_obj
                sermon.speaker_name = speaker_str
                sermon.category = category_obj
                sermon.series = series_obj
                sermon.save()

            synced_sermons_count += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {synced_sermons_count} messages/sermons."))

        # 5. SYNC REAL CHURCH EVENTS
        self.stdout.write("--> Syncing Church Events...")
        event_cat, _ = EventCategory.objects.get_or_create(
            name="Conferences & Special Services"
        )
        events_data = fetch_all("events")
        for ev in events_data:
            ev_title = (ev.get("title") or "").strip()
            if not ev_title:
                continue
            banner_url = ev.get("image") or ev.get("image_url") or ""
            desc = (ev.get("description") or f"Annual church convention and spiritual gathering: {ev_title}").strip()
            
            ev_date = datetime.now()
            if ev.get("date"):
                try:
                    ev_date = datetime.fromisoformat(ev.get("date").replace("Z", "+00:00"))
                except Exception:
                    pass

            ev_slug = slugify(ev_title)
            event, created = Event.objects.get_or_create(
                slug=ev_slug,
                defaults={
                    "title": ev_title,
                    "category": event_cat,
                    "tagline": f"Experience the power and glory of God at {ev_title}",
                    "description": desc,
                    "banner_image_url": banner_url,
                    "start_datetime": ev_date,
                    "status": PublishableStatus.PUBLISHED,
                    "is_featured": True,
                }
            )
            if not created:
                event.banner_image_url = banner_url
                event.save()

        self.stdout.write(self.style.SUCCESS("All mobile media, speakers, audio, and publications synced successfully!"))
