"""
Custom validators for ProjectsHub models.
"""
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


def validate_indian_phone(value):
    """
    Validate Indian phone numbers: +91XXXXXXXXXX or 10 digits starting with 6-9.
    Allows spaces, hyphens, and parentheses which are stripped before validation.
    """
    if not value:
        return
    
    pattern = r'^(\+91)?[6-9]\d{9}$'
    cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
    
    if not re.match(pattern, cleaned):
        raise ValidationError(
            'Enter a valid Indian phone number (10 digits starting with 6-9, optionally prefixed with +91).',
            code='invalid_phone'
        )


def validate_file_size(value):
    """
    Limit file uploads to 10MB to prevent storage abuse and slow uploads.
    """
    if not value:
        return
    
    limit = 10 * 1024 * 1024  # 10MB in bytes
    
    if hasattr(value, 'size') and value.size > limit:
        raise ValidationError(
            f'File size must not exceed 10 MB. Your file is {value.size / (1024 * 1024):.1f} MB.',
            code='file_too_large'
        )


# Slug validator for URL-safe strings
slug_validator = RegexValidator(
    regex=r'^[\w-]+$',
    message='Slug can only contain letters, numbers, hyphens, and underscores.',
    code='invalid_slug'
)


# URL slug validator (more permissive, allows forward slashes for paths)
path_validator = RegexValidator(
    regex=r'^[\w\-/]+$',
    message='Path can only contain letters, numbers, hyphens, underscores, and forward slashes.',
    code='invalid_path'
)
