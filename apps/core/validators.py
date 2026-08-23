"""
File upload validators for The CityGate Church platform.
Validates MIME types, extensions, and file sizes.
"""
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Maximum allowed file sizes in bytes
MAX_IMAGE_SIZE = 10 * 1024 * 1024       # 10 MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024     # 100 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024     # 500 MB
MAX_PDF_SIZE = 50 * 1024 * 1024        # 50 MB
MAX_DOCUMENT_SIZE = 30 * 1024 * 1024   # 30 MB

# Allowed extensions and MIME types
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif"]
ALLOWED_AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a", ".aac", ".ogg"]
ALLOWED_VIDEO_EXTENSIONS = [".mp4", ".webm", ".mov", ".mkv"]
ALLOWED_PDF_EXTENSIONS = [".pdf"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".txt"]

DANGEROUS_EXTENSIONS = [
    ".exe", ".bat", ".cmd", ".sh", ".php", ".py", ".pl", ".cgi", 
    ".js", ".vbs", ".msi", ".dll", ".scr", ".pif", ".wsf", ".apk"
]


def validate_file_safety(file_obj):
    """
    Ensure the file does not have a dangerous executable extension.
    """
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(_(f"File type '{ext}' is not allowed for security reasons."))


def validate_image_file(file_obj):
    validate_file_safety(file_obj)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(_(f"Invalid image extension '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"))
    if file_obj.size > MAX_IMAGE_SIZE:
        raise ValidationError(_(f"Image file size exceeds maximum limit of 10MB (file is {file_obj.size / (1024*1024):.1f}MB)."))


def validate_audio_file(file_obj):
    validate_file_safety(file_obj)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValidationError(_(f"Invalid audio extension '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"))
    if file_obj.size > MAX_AUDIO_SIZE:
        raise ValidationError(_(f"Audio file size exceeds maximum limit of 100MB (file is {file_obj.size / (1024*1024):.1f}MB)."))


def validate_video_file(file_obj):
    validate_file_safety(file_obj)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(_(f"Invalid video extension '{ext}'. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"))
    if file_obj.size > MAX_VIDEO_SIZE:
        raise ValidationError(_(f"Video file size exceeds maximum limit of 500MB (file is {file_obj.size / (1024*1024):.1f}MB)."))


def validate_pdf_file(file_obj):
    validate_file_safety(file_obj)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_PDF_EXTENSIONS:
        raise ValidationError(_("Only PDF files (.pdf) are allowed for this upload."))
    if file_obj.size > MAX_PDF_SIZE:
        raise ValidationError(_(f"PDF file size exceeds maximum limit of 50MB (file is {file_obj.size / (1024*1024):.1f}MB)."))
