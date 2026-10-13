import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend allowing login via either username or email address.
    Matches are case-insensitive and prioritize active superuser/staff accounts.
    Includes security enhancements: rate limiting, input validation, and audit logging.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')

        if not username or not password:
            return None

        username_str = str(username).strip()
        
        # Input validation - prevent injection attempts
        if len(username_str) > 150 or len(password) > 128:
            logger.warning(f"Authentication attempt with oversized credentials from {self._get_client_ip(request)}")
            return None
            
        # Basic input sanitization
        if not self._is_valid_username_format(username_str):
            logger.warning(f"Authentication attempt with invalid username format: {username_str[:50]}...")
            return None

        # Rate limiting protection
        if self._is_rate_limited(request, username_str):
            logger.warning(f"Rate limited authentication attempt for {username_str} from {self._get_client_ip(request)}")
            return None

        try:
            user = User.objects.filter(
                Q(username__iexact=username_str) | Q(email__iexact=username_str),
                is_active=True  # Only allow active users
            ).order_by('-is_superuser', '-is_staff', '-id').first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                # Clear rate limit on successful auth
                self._clear_rate_limit(request, username_str)
                
                # Log successful authentication for audit
                logger.info(f"Successful authentication for user {user.username} from {self._get_client_ip(request)}")
                return user
            else:
                # Track failed attempts
                self._track_failed_attempt(request, username_str)
                logger.warning(f"Failed authentication attempt for {username_str} from {self._get_client_ip(request)}")
                
        except Exception as e:
            logger.error(f"Authentication backend error: {e}")
            return None

        return None

    def _get_client_ip(self, request):
        """Get client IP address safely"""
        if not request:
            return 'unknown'
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')

    def _is_valid_username_format(self, username):
        """Validate username/email format to prevent injection"""
        # Allow alphanumeric, @, ., -, _ characters typical in usernames/emails
        return re.match(r'^[a-zA-Z0-9@._-]+$', username) is not None

    def _is_rate_limited(self, request, username):
        """Check if user/IP is rate limited"""
        if not request:
            return False
            
        ip = self._get_client_ip(request)
        
        # Check both IP and username-based rate limits
        ip_key = f"auth_attempts_ip:{ip}"
        user_key = f"auth_attempts_user:{username}"
        
        ip_attempts = cache.get(ip_key, 0)
        user_attempts = cache.get(user_key, 0)
        
        # Rate limits: 10 attempts per IP per 5 minutes, 5 per username per 5 minutes
        return ip_attempts >= 10 or user_attempts >= 5

    def _track_failed_attempt(self, request, username):
        """Track failed authentication attempts"""
        if not request:
            return
            
        ip = self._get_client_ip(request)
        
        ip_key = f"auth_attempts_ip:{ip}"
        user_key = f"auth_attempts_user:{username}"
        
        # Increment counters with 5-minute expiry
        cache.set(ip_key, cache.get(ip_key, 0) + 1, 300)
        cache.set(user_key, cache.get(user_key, 0) + 1, 300)

    def _clear_rate_limit(self, request, username):
        """Clear rate limiting on successful authentication"""
        if not request:
            return
            
        ip = self._get_client_ip(request)
        
        ip_key = f"auth_attempts_ip:{ip}"
        user_key = f"auth_attempts_user:{username}"
        
        cache.delete(ip_key)
        cache.delete(user_key)
