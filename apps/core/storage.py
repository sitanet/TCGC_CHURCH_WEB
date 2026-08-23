"""
Storage helpers and dynamic upload path generators.
"""
import os
import uuid
from datetime import datetime


def get_upload_path(instance, filename: str, subfolder: str = "general") -> str:
    """
    Generates a structured, date-partitioned upload path:
    uploads/<subfolder>/YYYY/MM/<uuid>.<ext>
    """
    ext = filename.split(".")[-1].lower() if "." in filename else "bin"
    unique_filename = f"{uuid.uuid4().hex[:12]}.{ext}"
    now = datetime.now()
    return os.path.join("uploads", subfolder, str(now.year), f"{now.month:02d}", unique_filename)


def sermon_audio_upload_path(instance, filename: str) -> str:
    return get_upload_path(instance, filename, subfolder="teachings/audio")


def sermon_cover_upload_path(instance, filename: str) -> str:
    return get_upload_path(instance, filename, subfolder="teachings/covers")


def publication_pdf_upload_path(instance, filename: str) -> str:
    return get_upload_path(instance, filename, subfolder="publications/documents")


def gallery_photo_upload_path(instance, filename: str) -> str:
    return get_upload_path(instance, filename, subfolder="media/gallery")


def event_banner_upload_path(instance, filename: str) -> str:
    return get_upload_path(instance, filename, subfolder="events/banners")
