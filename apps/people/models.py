"""
Models for Pastoral Leadership, Department Heads, and Ministers.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel


class LeadershipCategory(TimeStampedModel, SluggedModel, OrderedModel):
    name = models.CharField(_("category name"), max_length=100)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("Leadership Category")
        verbose_name_plural = _("Leadership Categories")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Person(TimeStampedModel, SluggedModel, PublishableModel, SEOModel, OrderedModel):
    """
    Pastoral team, council members, department leaders, or guest ministers.
    """
    name = models.CharField(_("full name with title"), max_length=150)
    title = models.CharField(_("ministry title"), max_length=150, help_text="e.g. Senior Pastor, Resident Pastor")
    category = models.ForeignKey(LeadershipCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="members")
    photo = models.ImageField(_("portrait photo"), upload_to="people/portraits/", blank=True, null=True)
    biography = models.TextField(_("full biography"), blank=True)
    email = models.EmailField(_("public ministry email"), blank=True)
    phone = models.CharField(_("contact phone"), max_length=50, blank=True)
    
    # Social links
    twitter_handle = models.CharField(_("Twitter / X handle"), max_length=100, blank=True)
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    instagram_url = models.URLField(_("Instagram URL"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)

    class Meta:
        verbose_name = _("Leader / Staff")
        verbose_name_plural = _("Leaders & Staff")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.title})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(self.name)
        super().save(*args, **kwargs)
