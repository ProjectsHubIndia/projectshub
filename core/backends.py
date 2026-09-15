from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend allowing login via either username or email address.
    Matches are case-insensitive and prioritize active superuser/staff accounts.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')

        if not username or not password:
            return None

        username_str = str(username).strip()
        try:
            user = User.objects.filter(
                Q(username__iexact=username_str) | Q(email__iexact=username_str)
            ).order_by('-is_superuser', '-is_staff', '-is_active', '-id').first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None

        return None
