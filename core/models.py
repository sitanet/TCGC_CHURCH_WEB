from django.db import models
from decimal import Decimal


class ConferenceRegistration(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    AGE_RANGE_CHOICES = [
        ('under_18', 'Under 18'),
        ('18_25', '18 - 25 years'),
        ('26_35', '26 - 35 years'),
        ('36_45', '36 - 45 years'),
        ('46_55', '46 - 55 years'),
        ('56_above', '56 years and above'),
    ]

    DESIGNATION_CHOICES = [
        ('student', 'Student'),
        ('working_professional', 'Working Professional'),
        ('business_owner', 'Business Owner / Entrepreneur'),
        ('minister_pastor', 'Minister / Pastor / Church Leader'),
        ('church_worker', 'TCGC Service Team'),
        ('job_seeker', 'Job Seeker'),
        ('retiree', 'Retiree'),
        ('other', 'Other'),
    ]

    ATTENDANCE_MODE_CHOICES = [
        ('camping', 'Camping (Residential On-site)'),
        ('non_camping', 'Non-Camping (Day Attendee)'),
        ('online', 'Online Streaming (Virtual)'),
        # Legacy aliases
        ('onsite_camp', 'Camping (Residential On-site)'),
        ('physical_day', 'Non-Camping (Day Attendee)'),
        ('virtual_streaming', 'Online Streaming (Virtual)'),
    ]

    FEEDING_SUBSCRIPTION_CHOICES = [
        ('lunch_dinner', 'Lunch & Dinner (Full Feeding)'),
        ('lunch_only', 'Lunch Only'),
        ('none', 'No Feeding Subscription (Self-Arranged)'),
    ]

    # Unique Registration Reference Code (e.g. IMGC-CAMP-78291, IMGC-LUNCH-48192, IMGC-REG-59102)
    registration_code = models.CharField(max_length=35, unique=True, db_index=True, blank=True, default='')

    # Personal Information
    surname = models.CharField(max_length=120)
    first_name = models.CharField(max_length=120)
    email = models.EmailField(db_index=True)
    phone_country_code = models.CharField(max_length=10, default='+234')
    phone_number = models.CharField(max_length=40, help_text="WhatsApp-enabled phone number")
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES)
    age_range = models.CharField(max_length=40, choices=AGE_RANGE_CHOICES)
    designation = models.CharField(max_length=100, choices=DESIGNATION_CHOICES)
    other_designation = models.CharField(max_length=120, blank=True, null=True, default='')

    # Location & Residence
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True, null=True, default='')
    country = models.CharField(max_length=120, default='Nigeria')

    # Conference Specifics
    is_first_time = models.BooleanField(default=False, verbose_name="First Time Attending IMGC?")
    first_time_attending = models.BooleanField(default=False)
    attendance_mode = models.CharField(
        max_length=40,
        choices=ATTENDANCE_MODE_CHOICES,
        default='camping',
    )
    feeding_subscription = models.CharField(
        max_length=30,
        choices=FEEDING_SUBSCRIPTION_CHOICES,
        default='none',
    )
    feeding_days = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        default='',
        help_text="Comma-separated selected days for meal subscription, e.g. Day 1, Day 2 or All Days",
    )
    expectation = models.TextField(blank=True, null=True, default='')
    special_notes = models.TextField(blank=True, null=True, default='', help_text="Expectations, dietary, medical or accommodation notes")

    # Processing & Verification (from TCGC_BACKEND IMGCRegistration)
    requires_code_dispatch = models.BooleanField(
        default=False,
        help_text="True if attendee subscribed for camping/meals and needs to send code",
    )
    dispatch_phone_target = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        help_text="Phone number attendee was instructed to send their code to",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Marked by admin when registration/payment is confirmed",
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        null=True,
        help_text="Amount paid for feeding/accommodation in NGN",
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional bank/transfer payment reference or receipt note",
    )
    has_checked_in = models.BooleanField(
        default=False,
        help_text="Marked when attendee checks in at the venue",
    )

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'imgc_registrations'
        managed = False
        ordering = ['-created_at']
        verbose_name = 'IMGC Conference Registration'
        verbose_name_plural = 'IMGC Conference Registrations'

    def __str__(self):
        code_prefix = f"{self.registration_code} - " if self.registration_code else ""
        return f"{code_prefix}{self.first_name} {self.surname} ({self.get_attendance_mode_display()})"

    @property
    def expectation(self):
        return self.special_notes or ''

    @expectation.setter
    def expectation(self, val):
        self.special_notes = val

    @property
    def first_time_attending(self):
        return self.is_first_time

    @first_time_attending.setter
    def first_time_attending(self, val):
        self.is_first_time = val

    @property
    def phone_country_code(self):
        if self.phone_number and self.phone_number.startswith('+'):
            return self.phone_number[:4]
        return '+234'

    def get_feeding_summary(self):
        """Human-readable feeding plan with selected days if applicable."""
        feeding_sub = getattr(self, 'feeding_subscription', 'none')
        feeding_days = getattr(self, 'feeding_days', '') or ''
        if feeding_sub == 'none':
            return "No Feeding (Self-Arranged)"
        elif feeding_sub == 'lunch_dinner':
            return "Lunch & Dinner (Full Feeding - All 5 Days)"
        elif feeding_sub == 'lunch_only':
            if feeding_days:
                if feeding_days.strip().lower() in (
                    'all',
                    'all days',
                    'all 5 days',
                    'day 1, day 2, day 3, day 4, day 5',
                    'day 1,day 2,day 3,day 4,day 5',
                ):
                    return "Lunch Only (All 5 Days)"
                return f"Lunch Only ({feeding_days})"
            return "Lunch Only (All 5 Days)"
        if hasattr(self, 'get_feeding_subscription_display'):
            return self.get_feeding_subscription_display()
        return str(feeding_sub)

    def has_meal_on_day(self, day_number):
        """Returns True if attendee has subscribed for meals on Day N (1, 2, 3, 4, 5)."""
        feeding_sub = getattr(self, 'feeding_subscription', 'none')
        feeding_days = getattr(self, 'feeding_days', '') or ''
        if feeding_sub == 'none':
            return False
        if feeding_sub == 'lunch_dinner':
            return True
        if feeding_sub == 'lunch_only':
            if not feeding_days or feeding_days.strip().lower() in ('all', 'all days', 'all 5 days', 'all_days', ''):
                return True
            day_str = f"day {day_number}"
            return day_str in feeding_days.lower() or str(day_number) in feeding_days
        return False

    @property
    def has_lunch_day_1(self):
        return self.has_meal_on_day(1)

    @property
    def has_lunch_day_2(self):
        return self.has_meal_on_day(2)

    @property
    def has_lunch_day_3(self):
        return self.has_meal_on_day(3)

    @property
    def has_lunch_day_4(self):
        return self.has_meal_on_day(4)

    @property
    def has_lunch_day_5(self):
        return self.has_meal_on_day(5)


# Alias for compatibility with TCGC_BACKEND IMGC logic
IMGCRegistration = ConferenceRegistration


class IMGCFeedingConfig(models.Model):
    """
    Configuration for IMGC feeding costs and payment settings (ported from TCGC_BACKEND).
    """
    service_team_daily_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1500.00'),
        help_text="Feeding cost per day for TCGC Service Team in NGN",
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Bank name for meal payment transfers",
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Bank account number",
    )
    account_name = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text="Bank account name",
    )
    payment_notes = models.TextField(
        blank=True,
        default='Please make transfer to the account above and use your Registration Code as payment reference.',
        help_text="Payment instructions displayed to workers",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'imgc_feeding_config'
        managed = False
        verbose_name = 'IMGC Feeding Configuration'
        verbose_name_plural = 'IMGC Feeding Configurations'

    def __str__(self):
        return f"IMGC Feeding Config (TCGC Service Team: ₦{self.service_team_daily_cost:,.2f}/day)"

    @classmethod
    def get_config(cls):
        """Safely fetch singleton config instance or return default without crashing."""
        try:
            config = cls.objects.first()
            if not config:
                config = cls.objects.create(
                    id=1,
                    service_team_daily_cost=Decimal('1500.00'),
                    bank_name='',
                    account_number='',
                    account_name='',
                )
            return config
        except Exception:
            class _FallbackConfig:
                service_team_daily_cost = Decimal('1500.00')
                bank_name = ''
                account_number = ''
                account_name = ''
                payment_notes = 'Please make transfer to the account above and use your Registration Code as payment reference.'
            return _FallbackConfig()


class OnlineGiving(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_country_code = models.CharField(max_length=10, default='+234')
    phone_number = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Online Giving Record'
        verbose_name_plural = 'Online Giving Records'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Testimony(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved / Published'),
        ('archived', 'Archived / Private'),
    ]

    CATEGORY_CHOICES = [
        ('healing', 'Healing & Miracle'),
        ('breakthrough', 'Financial Breakthrough / Provision'),
        ('salvation', 'Salvation & Spiritual Growth'),
        ('family', 'Family & Marriage Restoration'),
        ('career', 'Academic, Job & Career Promotion'),
        ('deliverance', 'Deliverance & Protection'),
        ('childbirth', 'Fruit of the Womb & Child Dedication'),
        ('general', 'Thanksgiving & Other Praises'),
    ]

    SHARE_CHOICES = [
        ('public', 'Share with My Name (Public)'),
        ('anonymous', 'Share Anonymously (Hide My Name)'),
        ('private', 'Private (Pastoral Team Only)'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=35, blank=True, null=True, help_text="WhatsApp or Mobile Phone")
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Nigeria')
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='general')
    title = models.CharField(max_length=200, help_text="Headline or brief title of your testimony")
    content = models.TextField(help_text="Detailed story of what God has done")
    share_preference = models.CharField(max_length=20, choices=SHARE_CHOICES, default='public')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'testimonies'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.full_name} ({self.get_category_display()})"

    @property
    def display_author(self):
        if self.share_preference == 'anonymous':
            return "Anonymous"
        return self.full_name

