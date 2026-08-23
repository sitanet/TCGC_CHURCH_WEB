"""
Custom User and Role models for The CityGate Church platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", _("Super Administrator")
    ADMIN = "admin", _("Administrator")
    PASTOR_STAFF = "pastor_staff", _("Pastoral Staff")
    CONTENT_MANAGER = "content_manager", _("Content Manager")
    MEDIA_LEAD = "media_lead", _("Media & Streaming Lead")
    EVENT_COORDINATOR = "event_coordinator", _("Event Coordinator")
    MEMBER = "member", _("Church Member / Volunteer")


class User(AbstractUser):
    """
    Custom user model providing role-based permissions,
    church title/department, and security metadata.
    """
    role = models.CharField(
        _("staff role"),
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.MEMBER,
        db_index=True,
    )
    title = models.CharField(_("title / ministry position"), max_length=100, blank=True)
    department = models.CharField(_("department / ministry"), max_length=100, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=30, blank=True)
    avatar = models.ImageField(_("profile photo"), upload_to="accounts/avatars/", blank=True, null=True)
    bio = models.TextField(_("biography"), max_length=1000, blank=True)
    is_verified = models.BooleanField(_("email verified"), default=False)
    
    # Audit tracking
    last_login_ip = models.GenericIPAddressField(_("last login IP"), blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username})"
        return self.username

    @property
    def is_super_admin(self) -> bool:
        return self.is_superuser or self.role == UserRole.SUPER_ADMIN

    @property
    def is_admin_user(self) -> bool:
        return self.is_super_admin or self.role == UserRole.ADMIN

    @property
    def is_pastoral_staff(self) -> bool:
        return self.is_admin_user or self.role == UserRole.PASTOR_STAFF

    @property
    def is_content_manager(self) -> bool:
        return self.is_admin_user or self.role in (UserRole.CONTENT_MANAGER, UserRole.PASTOR_STAFF)

    @property
    def is_media_lead(self) -> bool:
        return self.is_admin_user or self.role == UserRole.MEDIA_LEAD

    @property
    def is_event_coordinator(self) -> bool:
        return self.is_admin_user or self.role == UserRole.EVENT_COORDINATOR

    @property
    def is_staff_member(self) -> bool:
        """Determines if the user can access the administrative dashboard."""
        return self.is_staff or self.is_superuser or self.role != UserRole.MEMBER

    @property
    def role_display_badge(self) -> str:
        """Returns CSS badge modifier class for role."""
        badge_map = {
            UserRole.SUPER_ADMIN: "badge-danger",
            UserRole.ADMIN: "badge-gold",
            UserRole.PASTOR_STAFF: "badge-primary",
            UserRole.CONTENT_MANAGER: "badge-info",
            UserRole.MEDIA_LEAD: "badge-purple",
            UserRole.EVENT_COORDINATOR: "badge-success",
            UserRole.MEMBER: "badge-muted",
        }
        return badge_map.get(self.role, "badge-muted")
