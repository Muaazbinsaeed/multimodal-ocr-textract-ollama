import base64
import magic
from typing import BinaryIO
from fastapi import UploadFile
from PIL import Image
from io import BytesIO

from .config import settings
from .errors import ImageValidationError


def validate_file_type(file_content: bytes, filename: str) -> str:
    """Validate file type using magic bytes and return MIME type"""
    try:
        # Get MIME type from magic bytes
        mime_type = magic.from_buffer(file_content, mime=True)

        # Check if MIME type is allowed
        if mime_type not in settings.allowed_mime_types:
            allowed_types = ", ".join(settings.allowed_mime_types)
            raise ImageValidationError(
                f"File type '{mime_type}' not allowed. Supported types: {allowed_types}"
            )

        return mime_type

    except Exception as e:
        if isinstance(e, ImageValidationError):
            raise
        raise ImageValidationError(f"Unable to determine file type for '{filename}'")


def validate_file_size(file_content: bytes, filename: str) -> None:
    """Validate file size"""
    file_size = len(file_content)
    if file_size > settings.max_upload_bytes:
        max_mb = settings.max_upload_mb
        actual_mb = round(file_size / (1024 * 1024), 2)
        raise ImageValidationError(
            f"File '{filename}' is too large ({actual_mb}MB). Maximum size: {max_mb}MB"
        )

    if file_size == 0:
        raise ImageValidationError(f"File '{filename}' is empty")


def validate_image_content(file_content: bytes, filename: str) -> None:
    """Validate that the file is actually a valid image using Pillow"""
    try:
        with Image.open(BytesIO(file_content)) as img:
            # Try to load the image to verify it's valid
            img.verify()
    except Exception:
        raise ImageValidationError(f"File '{filename}' is not a valid image or is corrupted")


async def process_upload_file(file: UploadFile) -> tuple[bytes, str]:
    """Process uploaded file and return file content and MIME type"""
    if not file.filename:
        raise ImageValidationError("No file provided")

    # Read file content
    file_content = await file.read()

    # Validate file size
    validate_file_size(file_content, file.filename)

    # Validate file type using magic bytes
    mime_type = validate_file_type(file_content, file.filename)

    # Validate image content
    validate_image_content(file_content, file.filename)

    return file_content, mime_type


def encode_image_to_base64(image_content: bytes) -> str:
    """Encode image bytes to base64 string"""
    return base64.b64encode(image_content).decode('utf-8')


async def validate_and_encode_image(file: UploadFile) -> tuple[str, str]:
    """Complete pipeline: validate file and return base64 encoded image with MIME type"""
    file_content, mime_type = await process_upload_file(file)
    base64_image = encode_image_to_base64(file_content)
    return base64_image, mime_type