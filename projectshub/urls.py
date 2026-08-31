from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

admin.site.site_header = "AI ProjectsHub Admin"
admin.site.site_title = "AI ProjectsHub"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Serve user-uploaded media. This must come BEFORE the core URLs because
    # core.urls ends with a catch-all 404 route that would otherwise swallow
    # every /media/ request. It is also registered unconditionally (not only
    # when DEBUG) because the production host has no separate rule for /media/,
    # so uploads from the admin would return 404 there.
    re_path(
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),

    path('', include('core.urls')),
]
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
