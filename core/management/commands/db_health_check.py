"""
Management command to run database health checks.
Usage: python manage.py db_health_check
"""
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from io import StringIO


class Command(BaseCommand):
    help = 'Run database health checks: migrations, indexes, security, and statistics'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('ProjectsHub Database Health Check'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        
        # 1. Check migrations
        self.stdout.write('\n📋 Checking migrations...')
        out = StringIO()
        try:
            call_command('showmigrations', '--plan', stdout=out, verbosity=0)
            output = out.getvalue()
            pending = [line for line in output.split('\n') if '[ ]' in line]
            
            if pending:
                self.stdout.write(self.style.WARNING(f'⚠  {len(pending)} pending migrations found:'))
                for migration in pending[:5]:  # Show first 5
                    self.stdout.write(f'   {migration.strip()}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ All migrations applied'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Migration check failed: {e}'))
        
        # 2. Check deployment settings
        self.stdout.write('\n🔒 Checking deployment configuration...')
        out = StringIO()
        err = StringIO()
        try:
            call_command('check', '--deploy', stdout=out, stderr=err, verbosity=0)
            errors = err.getvalue()
            if errors and ('WARNING' in errors or 'ERROR' in errors):
                self.stdout.write(self.style.WARNING('⚠  Deployment warnings found:'))
                for line in errors.split('\n')[:5]:
                    if line.strip():
                        self.stdout.write(f'   {line.strip()}')
            else:
                self.stdout.write(self.style.SUCCESS('✓ Deployment checks passed'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠  Deployment check returned warnings'))
        
        # 3. Check database connection
        self.stdout.write('\n💾 Checking database connection...')
        try:
            with connection.cursor() as cursor:
                # Safe: Hardcoded health check query with no user input
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result == (1,):
                    db_name = connection.settings_dict.get('NAME', 'unknown')
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Database connected: {connection.vendor} ({db_name})'
                    ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))
            return
        
        # 4. Check cache table
        self.stdout.write('\n🗄️  Checking cache table...')
        try:
            with connection.cursor() as cursor:
                # Safe: Hardcoded queries with no user input
                if connection.vendor == 'sqlite':
                    cursor.execute(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='projectshub_cache'"
                    )
                    exists = cursor.fetchone()[0] > 0
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='projectshub_cache'"
                    )
                    exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # Safe: Hardcoded query with no user input
                    cursor.execute("SELECT COUNT(*) FROM projectshub_cache")
                    count = cursor.fetchone()[0]
                    self.stdout.write(self.style.SUCCESS(f'✓ Cache table exists: {count} entries'))
                else:
                    self.stdout.write(self.style.WARNING(
                        '⚠  Cache table missing. Run: python manage.py createcachetable'
                    ))
        except Exception:
            self.stdout.write(self.style.WARNING(
                '⚠  Cache table missing. Run: python manage.py createcachetable'
            ))
        
        # 5. Report key statistics
        self.stdout.write('\n📊 Database Statistics:')
        try:
            from core.models import Project, BlogPost, ContactInquiry, Page
            
            stats = [
                ('Projects', Project.objects.count(), Project.objects.filter(is_active=True).count()),
                ('Blog Posts', BlogPost.objects.count(), BlogPost.objects.filter(is_published=True).count()),
                ('Contact Inquiries', ContactInquiry.objects.count(), ContactInquiry.objects.filter(status='new').count()),
                ('Pages', Page.objects.count(), Page.objects.filter(status='published').count()),
            ]
            
            for label, total, active in stats:
                self.stdout.write(f'   {label}: {total} total, {active} active')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   Error loading statistics: {e}'))
        
        # 6. Check for common issues
        self.stdout.write('\n⚙️  Configuration Check:')
        
        # Secret key
        if not settings.SECRET_KEY or 'insecure' in settings.SECRET_KEY.lower():
            self.stdout.write(self.style.ERROR('   ✗ SECRET_KEY is insecure or missing'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ SECRET_KEY configured'))
        
        # Debug mode
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('   ⚠  DEBUG=True (should be False in production)'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ DEBUG=False'))
        
        # Allowed hosts
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            self.stdout.write(self.style.WARNING('   ⚠  ALLOWED_HOSTS not properly configured'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ ALLOWED_HOSTS: {len(settings.ALLOWED_HOSTS)} domains'))
        
        # Database backend
        self.stdout.write(f'   Database: {connection.vendor}')
        self.stdout.write(f'   Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
        
        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Health Check Complete'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
