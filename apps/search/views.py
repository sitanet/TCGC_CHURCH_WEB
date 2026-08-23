"""
Unified Search views across Sermons, Articles, Events, Publications, Ministries, and Leadership.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View


class UnifiedSearchApiView(APIView):
    """
    API endpoint returning unified search results categorized by content type.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query or len(query) < 2:
            return Response({
                "status": "success",
                "query": query,
                "results": {
                    "teachings": [],
                    "articles": [],
                    "events": [],
                    "publications": [],
                    "ministries": [],
                    "people": [],
                },
                "total_results": 0,
            })

        results = {
            "teachings": [],
            "articles": [],
            "events": [],
            "publications": [],
            "ministries": [],
            "people": [],
        }

        # Search Teachings
        try:
            from apps.teachings.models import Sermon
            sermons = Sermon.objects.filter(
                Q(title__icontains=query) |
                Q(speaker_name__icontains=query) |
                Q(summary__icontains=query) |
                Q(scripture_reference__icontains=query),
                status="published"
            )[:5]
            for s in sermons:
                results["teachings"].append({
                    "id": s.id,
                    "title": s.title,
                    "slug": s.slug,
                    "speaker": s.speaker_name,
                    "date": s.preached_date.isoformat() if s.preached_date else None,
                    "type": "teaching"
                })
        except Exception:
            pass

        # Search Articles
        try:
            from apps.articles.models import Article
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query),
                status="published"
            )[:5]
            for a in articles:
                results["articles"].append({
                    "id": a.id,
                    "title": a.title,
                    "slug": a.slug,
                    "author": a.display_author,
                    "type": "article"
                })
        except Exception:
            pass

        # Search Events
        try:
            from apps.events.models import Event
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue_name__icontains=query),
                status="published"
            )[:5]
            for e in events:
                results["events"].append({
                    "id": e.id,
                    "title": e.title,
                    "slug": e.slug,
                    "start": e.start_datetime.isoformat() if e.start_datetime else None,
                    "venue": e.venue_name,
                    "type": "event"
                })
        except Exception:
            pass

        # Search Publications
        try:
            from apps.publications.models import Publication
            publications = Publication.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                status="published"
            )[:5]
            for p in publications:
                results["publications"].append({
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "author": p.author_name,
                    "type": "publication"
                })
        except Exception:
            pass

        # Search Ministries
        try:
            from apps.ministries.models import Ministry
            ministries = Ministry.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query),
                status="published"
            )[:5]
            for m in ministries:
                results["ministries"].append({
                    "id": m.id,
                    "name": m.name,
                    "slug": m.slug,
                    "tagline": m.tagline,
                    "type": "ministry"
                })
        except Exception:
            pass

        # Search People
        try:
            from apps.people.models import Person
            people = Person.objects.filter(
                Q(name__icontains=query) |
                Q(title__icontains=query) |
                Q(biography__icontains=query),
                status="published"
            )[:5]
            for p in people:
                results["people"].append({
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "title": p.title,
                    "type": "person"
                })
        except Exception:
            pass

        total_count = sum(len(v) for v in results.values())
        return Response({
            "status": "success",
            "query": query,
            "results": results,
            "total_results": total_count,
        })
