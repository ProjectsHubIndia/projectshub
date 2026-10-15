"""
Management command to ensure an admin superuser exists.
Run with: python manage.py seed_admin

The password is read from --password or the ADMIN_PASSWORD environment variable.
An existing account's password is NEVER changed unless a password is given
explicitly, so a password set in the admin is not reverted on the next deploy.
If a brand-new account must be created and no password was provided, a random
one is generated and printed once (set a real one via the admin or ADMIN_PASSWORD).
"""
import os
import secrets

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Ensure the admin superuser exists (without resetting its password)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=os.environ.get('ADMIN_USERNAME', 'Harsh@123'))
        parser.add_argument('--email', type=str, default=os.environ.get('ADMIN_EMAIL', 'harsh@projectshub.co.in'))
        parser.add_argument('--password', type=str, default=None,
                            help='Admin password. Falls back to ADMIN_PASSWORD env var.')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or os.environ.get('ADMIN_PASSWORD') or None

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True},
        )
        # Keep the account usable as an admin, but leave an existing password alone.
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if not user.email:
            user.email = email

        if created and not password:
            password = secrets.token_urlsafe(16)
            self.stdout.write(self.style.WARNING(
                f'  [!] Generated a temporary password for new admin "{username}": {password}\n'
                f'      Change it in the admin or set ADMIN_PASSWORD, then rerun.'
            ))
        if password and (created or options['password'] or os.environ.get('ADMIN_PASSWORD')):
            user.set_password(password)

        user.save()
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] Superuser "{username}" {"created" if created else "verified (password unchanged)"}.'
        ))
