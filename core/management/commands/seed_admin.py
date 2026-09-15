"""
Management command to seed or update admin superuser credentials.
Run with: python manage.py seed_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Seed or update the admin superuser credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='Harsh@123',
            help='Admin username (default: Harsh@123)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123',
            help='Admin password (default: Admin@123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='harsh@projectshub.co.in',
            help='Admin email (default: harsh@projectshub.co.in)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        self.stdout.write(f'Seeding admin superuser credentials for "{username}"...')

        # Primary admin user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True}
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if not user.email:
            user.email = email
        user.save()

        action = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'  [OK] Superuser "{username}" successfully {action}.'))

        # Also ensure lowercase variant, standard 'admin', 'QA123', and 'harsh' are kept in sync if they exist
        sync_variants = ['admin', 'QA123', 'harsh']
        if username.lower() != username and username.lower() not in sync_variants:
            sync_variants.append(username.lower())

        for variant in sync_variants:
            try:
                var_user = User.objects.get(username=variant)
                var_user.set_password(password)
                var_user.is_staff = True
                var_user.is_superuser = True
                var_user.is_active = True
                var_user.save()
                self.stdout.write(self.style.SUCCESS(f'  [OK] Synced auxiliary account "{variant}" with current credentials.'))
            except User.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS('OK Admin login details seeded successfully!'))
