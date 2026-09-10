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
        return response
