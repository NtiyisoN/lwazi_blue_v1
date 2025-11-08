"""
Custom validators for file uploads and other validations
"""
from django.core.exceptions import ValidationError
from django.conf import settings
import os


def validate_file_size(file):
    """
    Validate that uploaded file doesn't exceed MAX_FILE_SIZE
    """
    max_size = getattr(settings, 'MAX_FILE_SIZE', 5 * 1024 * 1024)  # 5MB default
    
    if file.size > max_size:
        raise ValidationError(
            f'File size must not exceed {max_size // (1024 * 1024)}MB. '
            f'Your file is {file.size // (1024 * 1024)}MB.'
        )


def validate_image_extension(file):
    """
    Validate that uploaded image has an allowed extension
    """
    allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif'])
    ext = os.path.splitext(file.name)[1][1:].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension. Allowed: {", ".join(allowed_extensions)}'
        )


def validate_document_extension(file):
    """
    Validate that uploaded document has an allowed extension
    """
    allowed_extensions = getattr(settings, 'ALLOWED_DOCUMENT_EXTENSIONS', ['pdf', 'doc', 'docx', 'txt'])
    ext = os.path.splitext(file.name)[1][1:].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension. Allowed: {", ".join(allowed_extensions)}'
        )


def validate_file_content_type(file, allowed_types):
    """
    Validate file content type/MIME type
    """
    if hasattr(file, 'content_type'):
        if file.content_type not in allowed_types:
            raise ValidationError(
                f'Unsupported file type. Allowed: {", ".join(allowed_types)}'
            )

