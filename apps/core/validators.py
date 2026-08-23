"""
File upload validation and security utilities for The CityGate Church platform.
Prevents execution of malicious binaries, validates MIME/extension whitelists,
and enforces file size limits.
"""
import os
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_DOCUMENT_SIZE = 30 * 1024 * 1024   # 30 MB (PDFs, E-books)
MAX_AUDIO_SIZE = 100 * 1024 * 1024     # 100 MB (High-bitrate MP3)
MAX_VIDEO_SIZE = 500 * 1024 * 1024     # 500 MB (Direct video uploads)

# Whitelists
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".epub"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}

# Forbidden executable & script extensions
FORBIDDEN_EXTENSIONS = {
    ".exe", ".sh", ".bat", ".cmd", ".vbs", ".js", ".php", ".py", ".rb",
    ".pl", ".cgi", ".jar", ".msi", ".dll", ".so", ".bin", ".html", ".htm",
    ".phtml", ".svg", ".scr", ".com", ".pif"
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded filename to remove path traversal sequences and dangerous characters.
    """
    # Extract only the base name (strip directory paths)
    base_name = os.path.basename(filename)
    # Remove any character that isn't alphanumeric, dot, hyphen, or underscore
    clean_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", base_name)
    # Prevent leading dots (hidden files)
    clean_name = clean_name.lstrip(".")
    return clean_name or "upload"


def validate_file_extension(file_obj, allowed_extensions: set, label: str = "file"):
    """
    Ensure the uploaded file has an allowed extension and is not an executable script.
    """
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in FORBIDDEN_EXTENSIONS:
        raise ValidationError(
            _(f"Security Error: The file extension '{ext}' is forbidden for upload."),
            code="forbidden_extension"
        )
    if ext not in allowed_extensions:
        allowed_list = ", ".join(sorted(allowed_extensions))
        raise ValidationError(
            _(f"Invalid {label} format '{ext}'. Allowed formats are: {allowed_list}"),
            code="invalid_extension"
        )


def validate_file_size(file_obj, max_size_bytes: int, label: str = "file"):
    """
    Ensure the uploaded file does not exceed the allowed maximum size.
    """
    if file_obj.size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = file_obj.size / (1024 * 1024)
        raise ValidationError(
            _(f"The uploaded {label} ({actual_mb:.1f} MB) exceeds the maximum allowed size of {max_mb:.0f} MB."),
            code="file_too_large"
        )


def validate_image_file(file_obj):
    """
    Validator for image uploads (covers, portraits, gallery photos).
    """
    validate_file_extension(file_obj, ALLOWED_IMAGE_EXTENSIONS, label="image")
    validate_file_size(file_obj, MAX_IMAGE_SIZE, label="image")


def validate_pdf_file(file_obj):
    """
    Validator for publication PDFs and document uploads.
    """
    validate_file_extension(file_obj, ALLOWED_DOCUMENT_EXTENSIONS, label="document/PDF")
    validate_file_size(file_obj, MAX_DOCUMENT_SIZE, label="document/PDF")


validate_document_file = validate_pdf_file


def validate_audio_file(file_obj):
    """
    Validator for sermon audio broadcasts (MP3 / M4A).
    """
    validate_file_extension(file_obj, ALLOWED_AUDIO_EXTENSIONS, label="audio")
    validate_file_size(file_obj, MAX_AUDIO_SIZE, label="audio")


def validate_video_file(file_obj):
    """
    Validator for direct video message uploads (MP4 / WebM).
    """
    validate_file_extension(file_obj, ALLOWED_VIDEO_EXTENSIONS, label="video")
    validate_file_size(file_obj, MAX_VIDEO_SIZE, label="video")


def validate_file_safety(file_obj):
    """
    Generic media safety validator checking against forbidden executable extensions.
    """
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in FORBIDDEN_EXTENSIONS:
        raise ValidationError(
            _(f"Security Error: The file extension '{ext}' is forbidden for upload."),
            code="forbidden_extension"
        )
