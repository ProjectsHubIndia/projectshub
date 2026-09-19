from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from core.models import Redirect


class RedirectMiddleware(MiddlewareMixin):
    """
    Checks if the incoming request matches canonical domain rules (www to apex, HTTP to HTTPS)
    or any active custom Redirect rule from the database. Performs fast 301 / 302 redirects.
    """
    def process_request(self, request):
        path = request.path
        # Skip static assets and media to optimize performance
        if path.startswith(('/static/', '/media/', '/favicon.ico')):
            return None

        # 1. Canonical Domain & HTTPS Normalization
        host = request.get_host().lower().split(':')[0]
        if host == 'www.projectshub.co.in':
            target = f"https://projectshub.co.in{request.get_full_path()}"
            return HttpResponsePermanentRedirect(target)

        # Enforce HTTPS in production when accessed over plain HTTP
        if not request.is_secure() and host == 'projectshub.co.in' and getattr(settings, 'IS_PRODUCTION', False) and not settings.DEBUG:
            target = f"https://projectshub.co.in{request.get_full_path()}"
            return HttpResponsePermanentRedirect(target)

        # Seamlessly normalize /admin to /admin/ with query parameters preserved
        if path == '/admin':
            qs = request.META.get('QUERY_STRING', '')
            return HttpResponsePermanentRedirect(f'/admin/?{qs}' if qs else '/admin/')

        try:
            rule = Redirect.objects.filter(old_path=path, is_active=True).first()
            if not rule and not path.endswith('/'):
                rule = Redirect.objects.filter(old_path=f"{path}/", is_active=True).first()

            if rule:
                # Open redirect safeguard: ensure new_path is relative (not protocol-relative) or on allowed domain
                dest = rule.new_path.strip()
                if dest.startswith('//') or not (dest.startswith('/') or dest.startswith(('http://projectshub.co.in', 'https://projectshub.co.in', 'https://www.projectshub.co.in'))):
                    return None

                if rule.status_code == 301:
                    return HttpResponsePermanentRedirect(rule.new_path)
                return HttpResponseRedirect(rule.new_path)
        except Exception:
            # Pass silently if database tables are not yet initialized
            return None
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Ensures modern production security headers on all HTTP responses.
    """
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        
        # Enforce HSTS for secure or production requests
        if request.is_secure() or getattr(settings, 'IS_PRODUCTION', False) or 'projectshub.co.in' in request.get_host():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Defense-in-depth Content Security Policy
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = (
                "default-src 'self' https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.googletagmanager.com https://www.google-analytics.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https: https://www.google-analytics.com https://region1.google-analytics.com; "
                "frame-src 'self' https:; "
                "frame-ancestors 'self';"
            )
        return response

