"""
Production settings for The CityGate Church project.
"""
from .base import *

DEBUG = False

# Database Configuration (PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}

# HTTPS & Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "t")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email Backend (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "The CityGate Church <noreply@thecitygatechurch.org>")

# Storage (Pluggable Cloud Storage like AWS S3 / Cloudflare R2 if enabled)
USE_S3_STORAGE = os.getenv("USE_S3_STORAGE", "False").lower() in ("true", "1", "t")
if USE_S3_STORAGE:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME"),
                "region_name": os.getenv("AWS_S3_REGION_NAME", "us-east-1"),
                "custom_domain": os.getenv("AWS_S3_CUSTOM_DOMAIN"),
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
