"""
Management command for bulk data operations.
Provides CLI interface for common bulk operations on models.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from core.models import (
    ContactInquiry, ProjectGateLead, IdeaSubmission,
    WorkshopEnrollment, Project, BlogPost, ChatbotConversation
)


class Command(BaseCommand):
    help = 'Perform bulk operations on database records'

    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
            type=str,
            choices=[
                'mark_spam',
                'mark_contacted',
                'mark_converted',
                'archive_old',
                'delete_spam',
                'export_leads',
                'cleanup_old_chats',
                'publish_drafts',
                'unpublish_posts'
            ],
            help='Bulk operation to perform'
        )
        parser.add_argument(
            '--model',
            type=str,
            default='ContactInquiry',
            help='Model to operate on (ContactInquiry, ProjectGateLead, etc.)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days for time-based operations'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        operation = options['operation']
        model_name = options['model']
        days = options['days']
        confirm = options['confirm']
        dry_run = options['dry_run']

        # Get the model class
        model_map = {
            'ContactInquiry': ContactInquiry,
            'ProjectGateLead': ProjectGateLead,
            'IdeaSubmission': IdeaSubmission,
            'WorkshopEnrollment': WorkshopEnrollment,
            'Project': Project,
            'BlogPost': BlogPost,
            'ChatbotConversation': ChatbotConversation
        }

        if model_name not in model_map:
            raise CommandError(f'Invalid model: {model_name}')

        model = model_map[model_name]

        # Route to appropriate handler
        handlers = {
            'mark_spam': self.mark_as_spam,
            'mark_contacted': self.mark_as_contacted,
            'mark_converted': self.mark_as_converted,
            'archive_old': self.archive_old_records,
            'delete_spam': self.delete_spam_records,
            'export_leads': self.export_leads,
            'cleanup_old_chats': self.cleanup_old_chats,
            'publish_drafts': self.publish_drafts,
            'unpublish_posts': self.unpublish_posts
        }

        if operation in handlers:
            handlers[operation](model, days, confirm, dry_run)
        else:
            raise CommandError(f'Unknown operation: {operation}')

    def mark_as_spam(self, model, days, confirm, dry_run):
        """Mark old uncontacted leads as spam"""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        
        queryset = model.objects.filter(
            status='new',
            created_at__lt=cutoff
        )
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No records to mark as spam'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would mark {count} records as spam'
                )
            )
            return
        
        if not confirm:
            response = input(f'Mark {count} records as spam? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            updated = queryset.update(status='spam')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {updated} records as spam'
                )
            )

    def mark_as_contacted(self, model, days, confirm, dry_run):
        """Mark selected leads as contacted"""
        queryset = model.objects.filter(status='new')
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No new leads to mark'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would mark {count} leads as contacted'
                )
            )
            return
        
        if not confirm:
            response = input(f'Mark {count} leads as contacted? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            updated = queryset.update(status='contacted')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {updated} leads as contacted'
                )
            )

    def mark_as_converted(self, model, days, confirm, dry_run):
        """Mark contacted leads as converted"""
        queryset = model.objects.filter(status='contacted')
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No contacted leads to convert'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would mark {count} leads as converted'
                )
            )
            return
        
        if not confirm:
            response = input(f'Mark {count} leads as converted? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            updated = queryset.update(status='converted')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {updated} leads as converted'
                )
            )

    def archive_old_records(self, model, days, confirm, dry_run):
        """Archive old records (if model supports it)"""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        
        queryset = model.objects.filter(created_at__lt=cutoff)
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old records to archive'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would archive {count} records older than {days} days'
                )
            )
            return
        
        if not confirm:
            response = input(f'Archive {count} records older than {days} days? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        self.stdout.write(
            self.style.WARNING(
                f'Archive functionality not implemented for {model.__name__}. '
                'Consider exporting data first.'
            )
        )

    def delete_spam_records(self, model, days, confirm, dry_run):
        """Delete spam records permanently"""
        queryset = model.objects.filter(status='spam')
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No spam records to delete'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would permanently delete {count} spam records'
                )
            )
            return
        
        if not confirm:
            response = input(
                f'PERMANENTLY DELETE {count} spam records? This cannot be undone! [y/N]: '
            )
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            deleted, _ = queryset.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted} spam records'
                )
            )

    def export_leads(self, model, days, confirm, dry_run):
        """Export leads to CSV"""
        import csv
        from datetime import datetime
        
        queryset = model.objects.all().order_by('-created_at')
        
        if days:
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=cutoff)
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No records to export'))
            return
        
        filename = f'{model.__name__}_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would export {count} records to {filename}'
                )
            )
            return
        
        # Get field names
        field_names = [f.name for f in model._meta.get_fields() if not f.many_to_many and not f.one_to_many]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            
            for obj in queryset:
                row = {}
                for field in field_names:
                    value = getattr(obj, field, '')
                    row[field] = str(value) if value is not None else ''
                writer.writerow(row)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {count} records to {filename}'
            )
        )

    def cleanup_old_chats(self, model, days, confirm, dry_run):
        """Clean up old chat conversations"""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        
        if model != ChatbotConversation:
            self.stdout.write(
                self.style.ERROR('This operation only works with ChatbotConversation model')
            )
            return
        
        queryset = ChatbotConversation.objects.filter(
            updated_at__lt=cutoff,
            status='closed'
        )
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old chats to clean up'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would delete {count} chat conversations older than {days} days'
                )
            )
            return
        
        if not confirm:
            response = input(f'Delete {count} old chat conversations? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            deleted, _ = queryset.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted} old chat conversations'
                )
            )

    def publish_drafts(self, model, days, confirm, dry_run):
        """Publish draft blog posts or projects"""
        if not hasattr(model, 'is_published'):
            self.stdout.write(
                self.style.ERROR(f'{model.__name__} does not have is_published field')
            )
            return
        
        queryset = model.objects.filter(is_published=False)
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No drafts to publish'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would publish {count} draft records'
                )
            )
            return
        
        if not confirm:
            response = input(f'Publish {count} draft records? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            updated = queryset.update(is_published=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully published {updated} records'
                )
            )

    def unpublish_posts(self, model, days, confirm, dry_run):
        """Unpublish blog posts or projects"""
        if not hasattr(model, 'is_published'):
            self.stdout.write(
                self.style.ERROR(f'{model.__name__} does not have is_published field')
            )
            return
        
        queryset = model.objects.filter(is_published=True)
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No published records to unpublish'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would unpublish {count} published records'
                )
            )
            return
        
        if not confirm:
            response = input(f'Unpublish {count} published records? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Operation cancelled')
                return
        
        with transaction.atomic():
            updated = queryset.update(is_published=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully unpublished {updated} records'
                )
            )
