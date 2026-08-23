"""
Development settings for The CityGate Church project.
"""
from .base import *

DEBUG = True

# Database Configuration
# Default to PostgreSQL if specified in .env, or fallback to SQLite for local ease
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.postgresql")
DB_NAME = os.getenv("DB_NAME", "tcgc_church_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Check if PostgreSQL is explicitly disabled or SQLite is requested
USE_SQLITE = os.getenv("USE_SQLITE", "False").lower() in ("true", "1", "t")

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }

# Email Backend for Development (Console)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Static files development serving
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
