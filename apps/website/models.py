"""
Models for Communications, Inboxes, and Public Interactions (Contact, Prayer Requests, Newsletter).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel


class ContactMessageStatus(models.TextChoices):
    NEW = "new", _("New / Unread")
    READ = "read", _("Read")
    REPLIED = "replied", _("Replied")
    ARCHIVED = "archived", _("Archived")


class ContactMessage(TimeStampedModel):
    """
    Public inquiries submitted via the website contact form.
    """
    full_name = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("email address"))
    phone = models.CharField(_("phone number"), max_length=50, blank=True)
    subject = models.CharField(_("subject / inquiry type"), max_length=200, default="General Inquiry")
    message = models.TextField(_("message content"))
    
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ContactMessageStatus.choices,
        default=ContactMessageStatus.NEW,
        db_index=True,
    )
    admin_notes = models.TextField(_("internal staff notes"), blank=True)
    replied_at = models.DateTimeField(_("replied timestamp"), null=True, blank=True)

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.subject} ({self.created_at:%Y-%m-%d})"


class PrayerRequestStatus(models.TextChoices):
    NEW = "new", _("New")
    IN_PRAYER = "in_prayer", _("In Prayer / Intercession")
    HANDLED = "handled", _("Handled / Prayed For")
    ARCHIVED = "archived", _("Archived")


class PrayerRequest(TimeStampedModel):
    """
    Confidential prayer requests submitted by members and visitors.
    Staff-only access.
    """
    full_name = models.CharField(_("requester name"), max_length=150)
    email = models.EmailField(_("email address"), blank=True)
    phone = models.CharField(_("phone number"), max_length=50, blank=True)
    prayer_point = models.TextField(_("prayer request"))
    is_confidential = models.BooleanField(_("pastoral confidentiality only"), default=True)
    
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=PrayerRequestStatus.choices,
        default=PrayerRequestStatus.NEW,
        db_index=True,
    )
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_prayers",
        verbose_name=_("minister / pastor assigned"),
    )
    pastoral_notes = models.TextField(_("pastoral notes"), blank=True)

    class Meta:
        verbose_name = _("Prayer Request")
        verbose_name_plural = _("Prayer Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prayer from {self.full_name} ({self.created_at:%Y-%m-%d})"


class NewsletterSubscriber(TimeStampedModel):
    """
    Subscribers for church announcements, devotionals, and newsletters.
    """
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("subscriber name"), max_length=150, blank=True)
    is_active = models.BooleanField(_("is active"), default=True, db_index=True)
    subscribed_at = models.DateTimeField(_("subscribed at"), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_("unsubscribed at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
