"""
Public website views for The CityGate Church.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings


class HomeView(TemplateView):
    """
    Public landing page view.
    """
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "The CityGate Church — A Place of Divine Encounter"
        context["meta_description"] = (
            "Welcome to The CityGate Church. Experience inspiring teachings, "
            "vibrant worship, uplifting fellowship, and kingdom transformation."
        )
        return context


class AboutView(TemplateView):
    """
    About The CityGate Church (Vision, Mission, Leadership, Beliefs).
    """
    template_name = "website/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "About Us — The CityGate Church"
        context["meta_description"] = "Learn about our history, mission, spiritual heritage, and kingdom vision."
        return context


class VisitView(TemplateView):
    """
    Plan Your Visit (Service times, location directions, what to expect).
    """
    template_name = "website/visit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "Plan Your Visit — The CityGate Church"
        context["meta_description"] = "Join us this Sunday. Find our service schedules, location, parking, and children's church info."
        return context


class ContactView(TemplateView):
    """
    Contact and Prayer Request page.
    """
    template_name = "website/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "Contact & Prayer — The CityGate Church"
        return context
