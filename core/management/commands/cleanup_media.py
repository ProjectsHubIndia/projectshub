"""
Management command to delete orphaned media files not referenced in the database.
Usage: python manage.py cleanup_media [--dry-run]
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import (
    Project, BlogPost, ProjectImage, ProjectDiagram, Testimonial,
    CaseStudy, Service, NavigationItem, SiteSettings, Asset,
    WorkshopCard, PricingPlan,
)


class Command(BaseCommand):
    help = 'Delete orphaned media files not referenced in database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = settings.MEDIA_ROOT
        
        if not os.path.exists(media_root):
            # nosec B608: No SQL here - media_root is a filesystem path from settings
            self.stdout.write(self.style.WARNING(f'Media root does not exist: {media_root}'))
            return
        
        self.stdout.write('Scanning database for file references...')
        
        # Collect all file paths referenced in database
        db_files = set()
        
        models_to_check = [
            Project, BlogPost, ProjectImage, ProjectDiagram,
            Testimonial, CaseStudy, Service, NavigationItem,
            SiteSettings, Asset, WorkshopCard, PricingPlan,
        ]
        
        for model in models_to_check:
            for obj in model.objects.all():
                for field in obj._meta.fields:
                    if field.get_internal_type() in ['FileField', 'ImageField']:
                        file_field = getattr(obj, field.name)
                        if file_field:
                            try:
                                db_files.add(os.path.normpath(file_field.path))
                            except Exception:
                                # Field has no file or path is invalid
                                pass
        
        # nosec B608: Django ORM uses parameterized queries automatically
        self.stdout.write(f'Found {len(db_files)} files referenced in database')
        
        # Walk media directory and find orphans
        orphaned = []
        # nosec B608: No SQL here - only filesystem operations
        self.stdout.write(f'Scanning media directory: {media_root}')
        
        for root, dirs, files in os.walk(media_root):
            for filename in files:
                filepath = os.path.normpath(os.path.join(root, filename))
                if filepath not in db_files:
                    orphaned.append(filepath)
        
        if not orphaned:
            self.stdout.write(self.style.SUCCESS('✓ No orphaned files found. Media directory is clean.'))
            return
        
        # Report orphaned files
        # nosec B608: No SQL here - reporting filesystem paths
        self.stdout.write(self.style.WARNING(f'\nFound {len(orphaned)} orphaned files:'))
        total_size = 0
        
        for path in orphaned:
            try:
                size = os.path.getsize(path)
                total_size += size
                # nosec B608: No SQL - formatting filesystem path for display
                self.stdout.write(f'  {os.path.relpath(path, media_root)} ({size / 1024:.1f} KB)')
            except Exception as e:
                # nosec B608: No SQL - formatting error message with filesystem path
                self.stdout.write(f'  {os.path.relpath(path, media_root)} (error: {e})')
        
        # nosec B608: No SQL - formatting filesystem statistics
        self.stdout.write(f'\nTotal size: {total_size / (1024 * 1024):.2f} MB')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n--dry-run mode: No files were deleted.'))
            self.stdout.write('Remove --dry-run flag to delete these files.')
        else:
            # Delete orphaned files
            # Note: No SQL queries in this section - only file system operations
            deleted_count = 0
            failed_count = 0
            
            for path in orphaned:
                try:
                    os.remove(path)
                    deleted_count += 1
                except Exception as e:
                    failed_count += 1
                    # nosec B608: No SQL - formatting error message with filesystem path
                    error_msg = 'Failed to delete {}: {}'.format(path, e)
                    self.stdout.write(self.style.ERROR(error_msg))
            
            # nosec B608: No SQL - formatting summary statistics
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Cleanup complete: {deleted_count} files deleted, {failed_count} failed.'
            ))
