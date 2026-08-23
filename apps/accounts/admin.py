"""
Admin configuration for accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "title", "department")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Church Role & Details", {
            "fields": ("role", "title", "department", "phone_number", "avatar", "bio", "is_verified", "last_login_ip")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Church Role & Details", {
            "fields": ("role", "title", "department", "email")
        }),
    )
