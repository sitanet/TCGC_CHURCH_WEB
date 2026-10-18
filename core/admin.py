from django.contrib import admin
from .models import ConferenceRegistration, IMGCFeedingConfig, OnlineGiving, NewsletterSubscriber, Testimony


@admin.register(ConferenceRegistration)
class ConferenceRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'registration_code',
        'surname',
        'first_name',
        'email',
        'phone_number',
        'designation',
        'attendance_mode',
        'feeding_subscription',
        'feeding_days',
        'amount_paid',
        'is_verified',
        'has_checked_in',
        'created_at',
    )
    list_filter = (
        'attendance_mode',
        'feeding_subscription',
        'designation',
        'gender',
        'age_range',
        'is_first_time',
        'is_verified',
        'has_checked_in',
        'country',
    )
    search_fields = ('registration_code', 'surname', 'first_name', 'email', 'phone_number', 'city', 'state')


@admin.register(IMGCFeedingConfig)
class IMGCFeedingConfigAdmin(admin.ModelAdmin):
    list_display = ('service_team_daily_cost', 'bank_name', 'account_number', 'account_name', 'updated_at')


@admin.register(OnlineGiving)
class OnlineGivingAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_country_code', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)


@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_name', 'category', 'share_preference', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'category', 'share_preference', 'is_featured', 'created_at')
    search_fields = ('title', 'full_name', 'email', 'phone_number', 'content', 'city')

