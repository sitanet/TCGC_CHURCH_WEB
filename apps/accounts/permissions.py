"""
Permissions and Mixins for The CityGate Church platform.
"""
from functools import wraps
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework import permissions
from .models import UserRole


# ==============================================================================
# DJANGO VIEW MIXINS & DECORATORS
# ==============================================================================

class StaffRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated and is a church staff member.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff_member:
            messages.error(request, "Access restricted. You do not have staff permissions for this area.")
            return redirect("website:home")
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(AccessMixin):
    """
    Verify that the current user has one of the required roles.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in self.allowed_roles:
            messages.error(request, "You do not have permission to access this module.")
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)


def staff_required(view_func):
    """
    Decorator for views that checks if the user is a staff member.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_staff_member:
            raise PermissionDenied("Staff access required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles):
    """
    Decorator for views that requires specific staff roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN:
                return view_func(request, *args, **kwargs)
            if request.user.role not in allowed_roles:
                raise PermissionDenied("Insufficient permissions.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# ==============================================================================
# DJANGO REST FRAMEWORK PERMISSION CLASSES
# ==============================================================================

class IsStaffUser(permissions.BasePermission):
    """
    Allows access only to authenticated staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff_member)


class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to super administrators.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsContentManagerOrReadOnly(permissions.BasePermission):
    """
    Read permissions are allowed to any request,
    write permissions are only allowed to content managers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_content_manager)


class IsMediaLeadOrReadOnly(permissions.BasePermission):
    """
    Read permissions are allowed to any request,
    write permissions are only allowed to media leads.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_media_lead)
