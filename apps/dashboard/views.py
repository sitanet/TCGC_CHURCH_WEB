"""
Custom administrative dashboard views for The CityGate Church platform.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from apps.accounts.permissions import StaffRequiredMixin


class DashboardIndexView(StaffRequiredMixin, TemplateView):
    """
    Main executive & staff dashboard overview.
    Displays content stats, quick-access action drawers,
    and recent activity stream.
    """
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary counts (safe introspection)
        metrics = {
            "total_teachings": 0,
            "total_events": 0,
            "total_articles": 0,
            "total_media": 0,
            "total_publications": 0,
            "total_staff": 0,
        }

        try:
            from apps.accounts.models import User
            metrics["total_staff"] = User.objects.exclude(role="member").count()
        except Exception:
            pass

        try:
            from apps.teachings.models import Sermon
            metrics["total_teachings"] = Sermon.objects.count()
        except Exception:
            pass

        try:
            from apps.events.models import Event
            metrics["total_events"] = Event.objects.count()
        except Exception:
            pass

        try:
            from apps.articles.models import Article
            metrics["total_articles"] = Article.objects.count()
        except Exception:
            pass

        try:
            from apps.media_library.models import MediaAsset
            metrics["total_media"] = MediaAsset.objects.count()
        except Exception:
            pass

        try:
            from apps.publications.models import Publication
            metrics["total_publications"] = Publication.objects.count()
        except Exception:
            pass

        context["metrics"] = metrics
        return context
