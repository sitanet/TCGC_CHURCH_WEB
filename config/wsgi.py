"""
WSGI config for The CityGate Church project.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")
sys.path.insert(0, str(base_dir / "apps"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
