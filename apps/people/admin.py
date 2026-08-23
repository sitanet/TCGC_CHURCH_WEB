from django.contrib import admin
from .models import LeadershipCategory, Person


@admin.register(LeadershipCategory)
class LeadershipCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "category", "email", "status", "sort_order", "is_featured")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("name", "title", "biography")
    prepopulated_fields = {"slug": ("name",)}
