from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from core.models import Redirect


class RedirectMiddleware(MiddlewareMixin):
    """
    Checks if the incoming request path matches any active Redirect rule.
    Performs fast 301 / 302 redirects with zero overhead.
    """
    def process_request(self, request):
        path = request.path
        # Skip static assets and media to optimize performance
        if path.startswith(('/static/', '/media/', '/favicon.ico')):
            return None

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
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        
        # Defense-in-depth Content Security Policy
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = (
                "default-src 'self' https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'self';"
            )
        return response

