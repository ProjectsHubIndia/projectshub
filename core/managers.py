"""
Custom model managers for ProjectsHub.
"""
from django.db import models


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    Provides methods to access deleted records when needed.
    """
    
    def get_queryset(self):
        """Return only non-deleted records by default."""
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def with_deleted(self):
        """Include soft-deleted records in the queryset."""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=False)
