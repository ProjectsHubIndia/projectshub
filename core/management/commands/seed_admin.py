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

        # Ensure auxiliary superuser accounts and emails are always created and kept in sync
        auxiliary_accounts = {
            'admin': 'admin@projectshub.co.in',
            'QA123': 'Harsh@cmsminds.com',
            'harsh': 'Harsh@gmail.com',
            'harsh@123': 'harshsharmaqa@gmail.com',
        }
        if username.lower() != username and username.lower() not in auxiliary_accounts:
            auxiliary_accounts[username.lower()] = email

        for var_username, var_email in auxiliary_accounts.items():
            var_user, var_created = User.objects.get_or_create(
                username=var_username,
                defaults={'email': var_email, 'is_staff': True, 'is_superuser': True, 'is_active': True}
            )
            var_user.set_password(password)
            var_user.is_staff = True
            var_user.is_superuser = True
            var_user.is_active = True
            if not var_user.email and var_email:
                var_user.email = var_email
            var_user.save()
            action_label = 'created' if var_created else 'synced'
            self.stdout.write(self.style.SUCCESS(f'  [OK] {action_label.capitalize()} auxiliary account "{var_username}" ({var_user.email}).'))

        self.stdout.write(self.style.SUCCESS('OK Admin login details seeded successfully!'))
